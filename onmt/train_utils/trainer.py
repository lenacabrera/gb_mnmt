from __future__ import division


import datetime
import gc
import inspect
import math
import os
import re
import time
import torch
from apex import amp
from torchmetrics import F1Score, Precision, Recall
from torchmetrics.functional import accuracy

import onmt
import onmt.markdown
import onmt.modules
from onmt.data.data_iterator import DataIterator
from onmt.data.multidata_iterator import MultiDataIterator
from onmt.data.dataset import rewrap
from onmt.model_factory import build_model, build_language_model, optimize_model
from onmt.model_factory import init_model_parameters
from onmt.train_utils.stats import Logger
from onmt.utils import checkpoint_paths, normalize_gradients

from onmt.multiprocessing.multiprocessing_wrapper import MultiprocessingRunner

import sys

def varname(p):
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            return m.group(1)


def generate_data_iterator(dataset, seed, num_workers=1, epoch=1., buffer_size=0):

    # check if dataset is a list:
    if isinstance(dataset, list):
        # this is a multidataset
        data_iterator = MultiDataIterator(dataset, seed=seed, num_workers=num_workers,
                                          epoch=epoch, buffer_size=buffer_size)
    else:

        data_iterator = DataIterator(dataset, dataset.collater, dataset.batches, seed=seed,
                                     num_workers=num_workers, epoch=epoch, buffer_size=buffer_size)

    return data_iterator

class BaseTrainer(object):

    def __init__(self, model, loss_function, train_data, valid_data, dicts, opt):

        self.model = model
        self.train_data = train_data
        self.valid_data = valid_data
        self.dicts = dicts
        self.opt = opt
        self.cuda = (len(opt.gpus) >= 1 and opt.gpus[0] >= 0)

        self.loss_function = loss_function
        self.start_time = 0

        self.additional_data = []

    def add_additional_data(self, d, ratio):
        self.additional_data = d
        if ratio == "-1":
            self.additional_data_ratio = [1] * (len(self.additional_data + 1))
        else:
            self.additional_data_ratio = [int(s) for s in ratio.split(";")]
            assert (len(self.additional_data_ratio) == len(self.additional_data) + 1)

    def run(self, *args, **kwargs):

        raise NotImplementedError

    def eval(self, data):

        raise NotImplementedError

    def load_encoder_weight(self, checkpoint_file):

        print("Loading pretrained models from %s" % checkpoint_file)
        checkpoint = torch.load(checkpoint_file, map_location=lambda storage, loc: storage)

        pretrained_model = build_model(checkpoint['opt'], checkpoint['dicts'])
        pretrained_model.load_state_dict(checkpoint['model'])

        print("Loading pretrained encoder weights ...")
        pretrained_model.encoder.language_embedding = None
        enc_language_embedding = self.model.encoder.language_embedding
        self.model.encoder.language_embedding = None
        encoder_state_dict = pretrained_model.encoder.state_dict()

        self.model.encoder.load_state_dict(encoder_state_dict)
        self.model.encoder.language_embedding = enc_language_embedding
        return

    def load_decoder_weight(self, checkpoint_file):

        print("Loading pretrained models from %s" % checkpoint_file)
        checkpoint = torch.load(checkpoint_file, map_location=lambda storage, loc: storage)
        chkpoint_dict = checkpoint['dicts']

        pretrained_model = build_model(checkpoint['opt'], chkpoint_dict)
        pretrained_model.load_state_dict(checkpoint['model'])

        print("Loading pretrained decoder weights ...")
        # first we have to remove the embeddings which probably have difference size ...
        pretrained_word_emb = pretrained_model.decoder.word_lut
        pretrained_model.decoder.word_lut = None
        pretrained_lang_emb = pretrained_model.decoder.language_embeddings
        pretrained_model.decoder.language_embeddings = None

        # actually we assume that two decoders have the same language embeddings...
        untrained_word_emb = self.model.decoder.word_lut
        self.model.decoder.word_lut = None
        untrained_lang_emb = self.model.decoder.language_embeddings
        self.model.decoder.language_embeddings = None

        decoder_state_dict = pretrained_model.decoder.state_dict()
        self.model.decoder.load_state_dict(decoder_state_dict)

        # now we load the embeddings ....
        n_copies = 0
        for token in self.dicts['tgt'].labelToIdx:

            untrained_id = self.dicts['tgt'].labelToIdx[token]

            if token in chkpoint_dict['tgt'].labelToIdx:
                pretrained_id = chkpoint_dict['tgt'].labelToIdx[token]
                untrained_word_emb.weight.data[untrained_id].copy_(pretrained_word_emb.weight.data[pretrained_id])

                self.model.generator[0].linear.bias.data[untrained_id].copy_(pretrained_model
                                                                             .generator[0].linear.bias.data[
                                                                                 pretrained_id])
                n_copies += 1

        print("Copied embedding for %d words" % n_copies)
        self.model.decoder.word_lut = untrained_word_emb

        # now we load the language embeddings ...
        if pretrained_lang_emb and untrained_lang_emb and 'langs' in chkpoint_dict:
            for lang in self.dicts['langs']:

                untrained_id = self.dicts['langs'][lang]
                if lang in chkpoint_dict['langs']:
                    pretrained_id = chkpoint_dict['langs'][lang]
                    untrained_lang_emb.weight.data[untrained_id].copy_(pretrained_lang_emb.weight.data[pretrained_id])

        self.model.decoder.language_embeddings = untrained_lang_emb

    def _get_grads(self):
        grads = []
        for name, p in self.model.named_parameters():
            if not p.requires_grad:
                continue
            if p.grad is None:
                raise RuntimeError('Model parameter did not receive gradient: ' + name + '. '
                                                                                         'Use the param in the forward pass or set requires_grad=False.' +
                                   ' If you are using Stochastic model + fp16 - '
                                   'try to increase the number of minibatches' +
                                   ' each update to avoid uninitialized gradients.')
            grads.append(p.grad.data)
        return grads

    def _get_flat_grads(self, out=None):
        grads = self._get_grads()
        if out is None:
            grads_size = sum(g.numel() for g in grads)
            out = grads[0].new(
                grads_size).zero_()
        offset = 0
        for g in grads:
            numel = g.numel()
            out[offset:offset + numel].copy_(g.view(-1))
            offset += numel
        return out[:offset]

    def warm_up(self):
        """
        Warmup the memory allocator, by attempting to fit the largest batch
        :return:
        """
        if self.opt.memory_profiling:
            from pytorch_memlab import MemReporter
            reporter = MemReporter()
        
        batch = self.train_data[0].get_largest_batch() if isinstance(self.train_data, list) \
            else self.train_data.get_largest_batch()
        opt = self.opt

        if self.cuda:
            batch.cuda(fp16=self.opt.fp16 and not self.opt.fp16_mixed)
        # print("(trainer.py) self.model.train()()")
        self.model.train()
        self.model.zero_grad()
        oom = False

        if self.opt.memory_profiling:
            print("Input size: ")
            print(batch.size, batch.src_size, batch.tgt_size)

        if opt.streaming:
            streaming_state = self.model.init_stream()
        else:
            streaming_state = None

        try:
            targets = batch.get('target_output')
            tgt_mask = None
            outputs = self.model(batch, streaming=opt.streaming, target_mask=tgt_mask,
                                 zero_encoder=opt.zero_encoder,
                                 mirror=opt.mirror_loss, streaming_state=streaming_state)

            outputs['tgt_mask'] = tgt_mask

            loss_dict = self.loss_function(outputs, targets, model=self.model, vocab_mask=batch.vocab_mask)
            loss = loss_dict['loss']  # a little trick to avoid gradient overflow with fp16
            full_loss = loss

            if opt.mirror_loss:
                rev_loss = loss_dict['rev_loss']
                mirror_loss = loss_dict['mirror_loss']
                full_loss = full_loss + rev_loss + mirror_loss

            # reconstruction loss
            # if opt.reconstruct:
            #     rec_loss = loss_dict['rec_loss']
            #     rec_loss = rec_loss
            #     full_loss = full_loss + rec_loss
            #
            # if opt.lfv_multilingual:
            #     lid_logits = outputs['lid_logits']
            #     lid_labels = batch.get('target_lang')
            #     lid_loss_function = self.loss_function.get_loss_function('lid_loss')
            #     lid_loss = lid_loss_function(lid_logits, lid_labels)
            #     full_loss = full_loss + lid_loss

            optimizer = self.optim.optimizer

            if self.opt.memory_profiling:
                reporter.report(verbose=True)

                # for obj in gc.get_objects():
                #     try:
                #         if torch.is_tensor(obj) or (hasattr(obj, 'data') and torch.is_tensor(obj.data)):
                #             # print(varname(obj))
                #             # we can rule out parameter cost later
                #             # if 'parameter' not in type(obj):
                #             # if len(obj.shape) == 3:
                #             # if not isinstance(obj, torch.nn.parameter.Parameter):
                #             #     tensor = obj
                #             #     numel = tensor.
                #             print(type(obj), obj.type(), obj.size())
                #     except:
                #         pass

                # print("Memory profiling complete.")
                # print(torch.cuda.memory_summary())
                # exit()

            if self.cuda:
                with amp.scale_loss(full_loss, optimizer) as scaled_loss:
                    scaled_loss.backward()
            else:
                loss.div_(batch.tgt_size).backward()

            if self.opt.memory_profiling:
                print('========= after backward =========')
                reporter.report(verbose=True)

            self.model.zero_grad()
            self.optim.zero_grad()
            # self.optim.step()
            # self.optim.reset()

        except RuntimeError as e:
            if 'out of memory' in str(e):
                oom = True
            else:
                raise e

        if oom:
            print("* Warning: out-of-memory in warming up. This is due to the largest batch is too big for the GPU.")
        else:
            print("* Warming up successuflly.")

        if self.opt.memory_profiling:
            if hasattr(torch.cuda, 'memory_summary'):
                print(torch.cuda.memory_summary())
            exit()


class XETrainer(BaseTrainer):

    def __init__(self, model, loss_function, train_data, valid_data, dicts, opt, setup_optimizer=True, aux_loss_function=None):
        super().__init__(model, loss_function, train_data, valid_data, dicts, opt)

        self.n_gpus = len(self.opt.gpus)

        if self.cuda:
            torch.cuda.set_device(self.opt.gpus[0])
            torch.manual_seed(self.opt.seed)
            self.loss_function = self.loss_function.cuda()
            self.model = self.model.cuda()

        if setup_optimizer:

            self.optim = onmt.Optim(opt)
            self.optim.set_parameters(self.model.parameters())

            if not self.opt.fp16:
                opt_level = "O0"
                keep_batchnorm_fp32 = False
            elif self.opt.fp16_mixed:
                opt_level = "O1"
                keep_batchnorm_fp32 = None
            else:
                opt_level = "O2"
                keep_batchnorm_fp32 = False

            if self.cuda:
                self.model, self.optim.optimizer = amp.initialize(self.model,
                                                                  self.optim.optimizer,
                                                                  opt_level=opt_level,
                                                                  keep_batchnorm_fp32=keep_batchnorm_fp32,
                                                                  loss_scale="dynamic",
                                                                  verbosity=1)
        # An ugly hack to switch between align right and align left
        if hasattr(self.model, 'relative'):
            if self.model.relative:
                self.train_data.src_align_right = True
                self.train_data.tgt_align_right = False
                self.valid_data.src_align_right = True
                self.valid_data.tgt_align_right = False

        if aux_loss_function:
            self.aux_loss_function = aux_loss_function

    def save(self, epoch, valid_ppl, itr=None):

        opt = self.opt
        model = self.model
        dicts = self.dicts

        model_state_dict = self.model.state_dict()
        optim_state_dict = self.optim.state_dict()

        if itr:
            itr_state_dict = itr.state_dict()
        else:
            itr_state_dict = None

        #  drop a checkpoint
        checkpoint = {
            'model': model_state_dict,
            'dicts': dicts,
            'opt': opt,
            'epoch': epoch,
            'itr': itr_state_dict,
            'optim': optim_state_dict,
            'amp': amp.state_dict()
        }

        file_name = '%s_ppl_%.6f_e%.2f.pt' % (opt.save_model, valid_ppl, epoch)
        print('Writing to %s' % file_name)
        torch.save(checkpoint, file_name)

        # check the save directory here
        checkpoint_dir = os.path.dirname(opt.save_model)
        existed_save_files = checkpoint_paths(checkpoint_dir)
        for save_file in existed_save_files[opt.keep_save_files:]:
            print(" * Deleting old save file %s ...." % save_file)
            os.remove(save_file)

        best_epoch = float(re.search("_e(.*)\.pt", existed_save_files[0]).group(1))

        if epoch - best_epoch >= opt.early_stop_if_no_change:
            print(" * Early stopping at epoch %s as best epoch was %s ." % (epoch, best_epoch))
            sys.exit(0)

    def eval(self, data, report_classifier=False, report_cm=False, bidirectional_translation=False):
        total_loss = 0
        total_words = 0
        total_adv_loss = 0.0
        report_cm = True
        if self.opt.language_classifier or self.opt.gender_classifier:
            total_predict, correct_predict = 0.0, 0.0
            num_labels = self.model.generator[1].output_size
            res = torch.zeros(num_labels)

            if self.opt.gender_classifier:
                y_true, y_pred = [], []

            if report_cm:
                cm = torch.zeros([num_labels, num_labels], dtype=torch.long, device='cpu')

        total_src_words = 0.0
        opt = self.opt

        # batch_order = data.create_order(random=False)
        self.model.eval()
        self.model.reset_states()

        # the data iterator creates an epoch iterator
        data_iterator = generate_data_iterator(data, seed=self.opt.seed,
                                               num_workers=opt.num_workers, epoch=1, buffer_size=opt.buffer_size)
        epoch_iterator = data_iterator.next_epoch_itr(False, pin_memory=False)

        if opt.streaming:
            streaming_state = self.model.init_stream()
        else:
            streaming_state = None

        """ PyTorch semantics: save space by not creating gradients """
        data_size = len(epoch_iterator)
        i = 0

        with torch.no_grad():
            # for i in range(len(data)):
            while not data_iterator.end_of_epoch():
                # batch = data.next()[0]
                batch = next(epoch_iterator)
                if isinstance(batch, list):
                    batch = batch[0]
                batch = rewrap(batch)

                # batch = data.next()[0]

                # if opt.streaming:
                #     if data.is_new_stream():
                #         streaming_state = self.model.init_stream()
                # else:
                #     streaming_state = None

                if self.cuda:
                    batch.cuda(fp16=self.opt.fp16 and not self.opt.fp16_mixed)

                """ outputs can be either 
                        hidden states from decoder or
                        prob distribution from decoder generator
                """
                targets = batch.get('target_output')
                tgt_mask = targets.ne(onmt.constants.PAD)
                outputs = self.model(batch, streaming=opt.streaming, target_mask=tgt_mask,
                                     mirror=opt.mirror_loss, streaming_state=streaming_state)

                if opt.streaming:
                    streaming_state = outputs['streaming_state']

                outputs['tgt_mask'] = tgt_mask

                # normal loss
                loss_dict = self.loss_function(outputs, targets, model=self.model)
                loss_data = loss_dict['data']

                total_loss += loss_data
                total_words += batch.tgt_size

                total_src_words += batch.src_size

                if bidirectional_translation:
                    targets = batch.get('source_output')    # (T, B)
                    tgt_mask = targets.ne(onmt.constants.PAD)
                    outputs_rev = self.model(batch, streaming=opt.streaming, target_mask=tgt_mask,
                                             mirror=opt.mirror_loss, streaming_state=streaming_state, reverse_src_tgt=True)
                    outputs_rev['tgt_mask'] = tgt_mask
                    # normal loss
                    loss_dict = self.loss_function(outputs_rev, targets, model=self.model)
                    loss_data = loss_dict['data']
                    total_loss += loss_data
                    # flipped since src and tgt are now flipped
                    total_words += batch.src_size
                    total_src_words += batch.tgt_size

                # adv loss
                if opt.language_classifier and opt.language_classifier_tok:
                    if opt.token_classifier == 0:
                        # predict language ID
                        targets_classifier = batch.get('targets_source_lang')  # starts from 1 (0 is padding)
                    elif opt.token_classifier == 1:
                        # predict source token ID
                        targets_classifier = batch.get('source')  # starts from 0 (padding), real tokens starts from 1
                    elif opt.token_classifier == 2:
                        # predict positional ID
                        targets_classifier = batch.get('source_pos')
                        targets_classifier[targets_classifier != 0] += 1  # start from 0
                        targets_classifier[0, :] += 1
                    else:
                        raise NotImplementedError

                    classifier_loss_dict = self.loss_function(outputs, targets=targets_classifier, model=self.model,
                                                              lan_classifier=True)
                    classifier_loss_data = classifier_loss_dict['data'] if classifier_loss_dict['data'] is not None else 0
                    total_adv_loss += classifier_loss_data

                    if bidirectional_translation:
                        if opt.token_classifier == 0:
                            # predict language ID
                            targets_classifier_rev = batch.get('targets_target_lang')  # starts from 1 (0 is padding)
                        elif opt.token_classifier == 1:
                            # predict source token ID
                            targets_classifier_rev = batch.get('target')  # starts from 0 (padding), real tokens starts from 1
                        elif opt.token_classifier == 2:
                            # predict positional ID
                            targets_classifier_rev = batch.get('target_pos')
                            targets_classifier_rev[targets_classifier_rev != 0] += 1  # start from 0
                            targets_classifier_rev[0, :] += 1
                        else:
                            raise NotImplementedError

                        classifier_loss_dict = self.loss_function(outputs_rev, targets=targets_classifier_rev, model=self.model,
                                                                  lan_classifier=True)
                        classifier_loss_data += classifier_loss_dict['data']
                        total_adv_loss += classifier_loss_data

                    if opt.token_classifier is not None and report_classifier:
                        logprobs_lan = outputs['logprobs_lan']
                        logprobs_lan = logprobs_lan.masked_fill(outputs['src_mask'].permute(2, 0, 1),
                                                                           onmt.constants.PAD).type_as(logprobs_lan)
                        pred = logprobs_lan  # T, B, V

                        pred_idx = torch.argmax(pred, dim=-1).cpu()  # T, B. starts from 0
                        correct_idx = (targets_classifier.cpu() - 1 == pred_idx) # padding not counted, since 0 - 1 would be -1

                        correct_predict += correct_idx.sum()
                        total_predict += (~outputs['src_mask']).sum()

                        if bidirectional_translation:
                            logprobs_lan = outputs_rev['logprobs_lan']
                            logprobs_lan = logprobs_lan.masked_fill(outputs_rev['src_mask'].permute(2, 0, 1),
                                                                    onmt.constants.PAD).type_as(logprobs_lan)
                            pred = logprobs_lan  # T, B, V

                            pred_idx_rev = torch.argmax(pred, dim=-1).cpu()  # T, B. starts from 0
                            correct_idx_rev = (targets_classifier_rev.cpu() - 1 == pred_idx_rev)

                            correct_predict += correct_idx_rev.sum()
                            total_predict += (~outputs_rev['src_mask']).sum()

                        if report_cm:
                            all_cnt = []
                            if opt.token_classifier == 0:   # language label starts from 1
                                label_range = torch.arange(1, num_labels + 1)
                            else:
                                label_range = torch.arange(num_labels)

                            for p in label_range:  # 1, 2, 3, 4
                                cur_label_indx = (targets_classifier == p)  # those positions with this current label
                                pred_val, pred_cnt = torch.unique(pred_idx[cur_label_indx], return_counts=True)

                                if pred_val.shape[0] < num_labels:  # not all labels have been predicted
                                    pred_cnt_padded = torch.zeros(num_labels, dtype=torch.long, device='cpu')
                                    pred_cnt_padded[pred_val] = pred_cnt
                                    pred_cnt = pred_cnt_padded
                                elif pred_val.shape[0] > num_labels:
                                    raise ValueError('Some impossible label was predicted. Check your label esp. indexing.')

                                all_cnt.append(pred_cnt)

                            if bidirectional_translation:
                                for p in label_range:  # 1, 2, 3, 4
                                    cur_label_indx = (targets_classifier_rev == p)
                                    pred_val, pred_cnt = torch.unique(pred_idx_rev[cur_label_indx], return_counts=True)
                                    if pred_val.shape[0] < num_labels:  # not all labels have been predicted
                                        pred_cnt_padded = torch.zeros(num_labels, dtype=torch.long, device='cpu')
                                        pred_cnt_padded[pred_val] = pred_cnt
                                        pred_cnt = pred_cnt_padded
                                    elif pred_val.shape[0] > num_labels:
                                        raise ValueError('Some impossible label was predicted. Check your label esp. indexing.')

                                    all_cnt[p-1] += pred_cnt

                            res_per_row = torch.stack(all_cnt, dim=0)
                            cm.index_add_(0, torch.arange(num_labels, device='cpu'), res_per_row)


                # gender classifier
                if opt.gender_classifier: # and opt.gender_classifier_tok:
                    targets_classifier = batch.get('gen') 

                    classifier_loss_dict = self.loss_function(outputs, targets=targets_classifier, model=self.model,
                                                              gen_classifier=True, gen_classifier_sent=opt.gender_classifier_sent)
                    classifier_loss_data = classifier_loss_dict['data'] if classifier_loss_dict['data'] is not None else 0
                    total_adv_loss += classifier_loss_data

                    # if bidirectional_translation:
                    #     # TODO lena, change
                    #     # raise NotImplementedError
                    #     targets_classifier_rev = batch.get('targets_source_gen') # gen

                    #     classifier_loss_dict = self.loss_function(outputs_rev, targets=targets_classifier_rev, model=self.model,
                    #                                               gen_classifier=True)
                    #     classifier_loss_data += classifier_loss_dict['data']
                    #     total_adv_loss += classifier_loss_data

                    if opt.gender_classifier is not None and report_classifier:
                        # probabilities per class (0: neuter, 1: masculine, 2: feminine)
                        logprobs_gen = outputs['logprobs_gen']
                        pred = logprobs_gen  # T, B, V

                        if opt.gender_classifier_sent:
                            pred = pred.squeeze()
                            targets_classifier = targets_classifier.squeeze()

                        # argmax indices
                        pred_idx = torch.argmax(pred, dim=-1).cpu()  # T, B. starts from 0
                        y_pred.extend(pred_idx[targets_classifier > 0].flatten().cpu())

                        # correct indices
                        correct_idx = (targets_classifier.cpu() - 1 == pred_idx) # padding not counted, since 0 - 1 would be -1

                        # store results (counts)
                        correct_predict += correct_idx.sum()
                        total_predict += (torch.flatten(targets_classifier) != 0).nonzero().size()[0]

                        # targets (without padding)
                        y_true.extend((targets_classifier[targets_classifier > 0]).flatten() - 1)

                        # print("(trainer.py) logprobs_gen.size(): ", logprobs_gen.size())
                        # print("(trainer.py) targets_classifier.size(): ", targets_classifier.size())
                        # print("(trainer.py) pred_idx.size(): ", pred_idx.size())


                        # if bidirectional_translation:
                        #     logprobs_gen = outputs_rev['logprobs_gen']
                        #     # logprobs_gen = logprobs_gen.masked_fill(outputs_rev['src_mask'].permute(2, 0, 1),
                        #     #                                         onmt.constants.PAD).type_as(logprobs_gen)
                        #     pred = logprobs_gen  # T, B, V

                        #     pred_idx_rev = torch.argmax(pred, dim=-1).cpu()  # T, B. starts from 0
                        #     correct_idx_rev = (targets_classifier_rev.cpu() - 1 == pred_idx_rev)

                        #     correct_predict += correct_idx_rev.sum()
                        #     total_predict += targets_classifier_rev.size()[0]  
                        #     # total_predict += (~outputs_rev['src_mask']).sum()

                        if report_cm:
                            all_cnt = []
                            if opt.gender_token_classifier == 0:   
                                label_range = torch.arange(1, num_labels + 1)  # gender label starts from 1
                            else:
                                label_range = torch.arange(num_labels)

                            for p in label_range:  # 1, 2, 3, 4
                                cur_label_indx = (targets_classifier == p)  # those positions with this current label
                                pred_val, pred_cnt = torch.unique(pred_idx[cur_label_indx], return_counts=True)
                                if pred_val.shape[0] < num_labels:  # not all labels have been predicted
                                    pred_cnt_padded = torch.zeros(num_labels, dtype=torch.long, device='cpu')
                                    pred_cnt_padded[pred_val] = pred_cnt
                                    pred_cnt = pred_cnt_padded
                                    print("not all labels have been predicted, pred_cnt: ", pred_cnt)
                                elif pred_val.shape[0] > num_labels:
                                    raise ValueError('Some impossible label was predicted. Check your label esp. indexing.')

                                all_cnt.append(pred_cnt)

                            # if bidirectional_translation:
                            #     for p in label_range:  # 1, 2, 3, 4
                            #         cur_label_indx = (targets_classifier_rev == p)
                            #         pred_val, pred_cnt = torch.unique(pred_idx_rev[cur_label_indx], return_counts=True)
                            #         if pred_val.shape[0] < num_labels:  # not all labels have been predicted
                            #             pred_cnt_padded = torch.zeros(num_labels, dtype=torch.long, device='cpu')
                            #             pred_cnt_padded[pred_val] = pred_cnt
                            #             pred_cnt = pred_cnt_padded
                            #         elif pred_val.shape[0] > num_labels:
                            #             raise ValueError('Some impossible label was predicted. Check your label esp. indexing.')

                            #         all_cnt[p-1] += pred_cnt

                            res_per_row = torch.stack(all_cnt, dim=0)
                            # print("(trainer.py) res_per_row: ", res_per_row)
                            cm.index_add_(0, torch.arange(num_labels, device='cpu'), res_per_row)
                

            if (opt.token_classifier is not None or opt.gender_token_classifier is not None) and report_classifier:
                print("*************************************************************************")
                # print("(trainer.py) correct_predict, total_predict: ", correct_predict, total_predict)
                if opt.language_classifier:
                    print('Classifier accuracy', (correct_predict / total_predict).data.item())
                
                if opt.gender_classifier:
                    # gender (f/m) specific metrics
                    _y_true = torch.tensor(y_true, dtype=torch.int32, device=torch.device('cpu'))
                    _y_pred = torch.tensor(y_pred, dtype=torch.int32, device=torch.device('cpu'))
                    n_cor_n = (_y_pred[_y_true == 0].flatten() == 0).nonzero(as_tuple=False).size()[0]
                    n_cor_m = (_y_pred[_y_true == 1].flatten() == 1).nonzero().size()[0]
                    n_cor_f = (_y_pred[_y_true == 2].flatten() == 2).nonzero().size()[0]
                    n_tar_n = (_y_true.flatten() == 0).nonzero().size()[0]
                    n_tar_m = (_y_true.flatten() == 1).nonzero().size()[0]
                    n_tar_f = (_y_true.flatten() == 2).nonzero().size()[0]

                    num_classes = None
                    if opt.gender_classifier_tok:
                        num_classes = 3
                    else:
                        num_classes=2

                    f1 = F1Score(num_classes=num_classes, average="none")(_y_true, _y_pred)
                    f1_w = F1Score(num_classes=num_classes, average="weighted")(_y_true, _y_pred)
                    precision = Precision(num_classes=num_classes, average="none")(_y_true, _y_pred)
                    recall = Recall(num_classes=num_classes, average="none")(_y_true, _y_pred)
                    print('Classifier accuracy (n m f)  ', (n_cor_n + n_cor_m + n_cor_f) / (n_tar_n + n_tar_m + n_tar_f))

                    if opt.gender_classifier_tok:
                        print('Classifier accuracy (n/m/f)  ', torch.true_divide(cm[0][0], cm[0].sum()).item(), torch.true_divide(cm[1][1], cm[1].sum()).item(), torch.true_divide(cm[2][2], cm[2].sum()).item())
                        print('Classifier F1 score (n/m/f)  ', f1[0].item(), f1[1].item(), f1[2].item())

                        print('Classifier Precision (n/m/f) ', precision[0].item(), precision[1].item(), precision[2].item())
                        print('Classifier Recall (n/m/f)    ', recall[0].item(), recall[1].item(), recall[2].item())
                        print('Classifier w. F1  (n/m/f)    ', f1_w.item())

                    else:
                        print('Classifier accuracy (m/f)  ', torch.true_divide(cm[0][0], cm[0].sum()).item(), torch.true_divide(cm[1][1], cm[1].sum()).item())
                        print('Classifier F1 score (m/f)  ', f1[0].item(), f1[1].item())
                        print('Classifier w. F1  (n/m/f)    ', f1_w.item())

                if report_cm:
                    print(cm.cpu().numpy())
                    cm = torch.true_divide(cm, cm.sum(dim=1, keepdim=True)) # divided over true
                    cm2 = torch.true_divide(cm, cm.sum(dim=0, keepdim=True))    # divided over predicted
                    cm3 = 2 * torch.true_divide((cm * cm2), (cm + cm2))
                    print('Confusion matrix, precision (row: true, col: pred):\n', cm.cpu().numpy())
                    print('Confusion matrix, recall (row: true, col: pred):\n', cm2.cpu().numpy())
                    print('Confusion matrix, F1 (row: true, col: pred):\n', cm3.cpu().numpy())
                
                print("*************************************************************************")

        self.model.train()
        return total_loss / total_words, total_adv_loss / total_src_words

    def train_epoch(self, epoch, resume=False, itr_progress=None):
        global rec_ppl
        opt = self.opt
        train_data = self.train_data
        streaming = opt.streaming

        # Clear the gradients of the model
        # self.runner.zero_grad()
        self.model.zero_grad()
        self.model.reset_states()

        dataset = train_data

        data_iterator = generate_data_iterator(dataset, seed=self.opt.seed, num_workers=opt.num_workers,
                                               epoch=epoch, buffer_size=opt.buffer_size)

        if resume:  # previously working with batch_order=None, iteration=0
            data_iterator.load_state_dict(itr_progress)

        epoch_iterator = data_iterator.next_epoch_itr(not streaming, pin_memory=opt.pin_memory)

        total_tokens, total_loss, total_words = 0, 0, 0
        total_non_pads = 0
        report_loss, report_tgt_words = 0, 0
        report_classifier_loss, report_classifier_loss_rev = 0.0, 0.0
        report_aux_loss = 0.0
        report_src_words = 0
        start = time.time()
        n_samples = len(train_data)

        counter = 0
        update_counter = 0
        num_accumulated_words = 0
        num_accumulated_sents = 0
        denom = 3584
        nan = False

        if opt.streaming:
            streaming_state = self.model.init_stream()
        else:
            streaming_state = None

        i = data_iterator.iterations_in_epoch if not isinstance(train_data, list) else epoch_iterator.n_yielded

        while not data_iterator.end_of_epoch():
            curriculum = (epoch < opt.curriculum)

            # this batch generator is not very clean atm
            batch = next(epoch_iterator)
            if isinstance(batch, list) and self.n_gpus == 1:
                batch = batch[0]
            batch = rewrap(batch)

            if self.cuda:
                batch.cuda(fp16=self.opt.fp16 and not self.opt.fp16_mixed)

            oom = False
            try:
                # outputs is a dictionary containing keys/values necessary for loss function
                # can be flexibly controlled within models for easier extensibility
                targets = batch.get('target_output')
                tgt_mask = targets.data.ne(onmt.constants.PAD)

                outputs = self.model(batch, streaming=opt.streaming, target_mask=tgt_mask,
                                     zero_encoder=opt.zero_encoder,
                                     mirror=opt.mirror_loss, streaming_state=streaming_state)

                batch_size = batch.size

                outputs['tgt_mask'] = tgt_mask

                loss_dict = self.loss_function(outputs, targets, model=self.model)
                loss_data = loss_dict['data']
                loss = loss_dict['loss'].div(denom)  # a little trick to avoid gradient overflow with fp16

                optimizer = self.optim.optimizer

                has_classifier_loss = (self.opt.token_classifier is not None and not self.opt.freeze_language_classifier) or \
                    (self.opt.gender_token_classifier is not None) # and not self.opt.freeze_language_classifier)
                use_aux_loss = epoch >= self.opt.aux_loss_start_from

                if not has_classifier_loss:
                    # calculate gradient for enc / dec
                    # if not self.opt.bidirectional_translation:
                    if self.cuda:
                        with amp.scale_loss(loss, optimizer) as scaled_loss:
                            scaled_loss.backward(retain_graph=self.opt.bidirectional_translation)
                    else:
                        loss.backward(retain_graph=self.opt.bidirectional_translation)

                    if self.opt.bidirectional_translation:
                        # translate tgt -> src
                        outputs_rev = self.model(batch, streaming=opt.streaming, target_mask=tgt_mask,
                                                 zero_encoder=opt.zero_encoder,
                                                 mirror=opt.mirror_loss, streaming_state=streaming_state,
                                                 reverse_src_tgt=True)
                        batch_size += batch.tgt_size
                        targets = batch.get('source_output')
                        src_mask = targets.data.ne(onmt.constants.PAD)
                        outputs_rev['tgt_mask'] = src_mask

                    # if self.opt.bidirectional_translation:
                        loss_dict = self.loss_function(outputs_rev, targets, model=self.model)
                        loss_data += loss_dict['data']
                        loss = loss_dict['loss'].div(denom)  # a little trick to avoid gradient overflow with fp16

                        if self.cuda:
                            with amp.scale_loss(loss, optimizer) as scaled_loss:
                                scaled_loss.backward(retain_graph=use_aux_loss)
                        else:
                            loss.backward(retain_graph=use_aux_loss)

                        if use_aux_loss and self.aux_loss_function:
                            if opt.sim_loss_update_one is None:
                                aux_loss_dict = self.aux_loss_function(outputs_rev['context'], outputs['context'],
                                                                       outputs_rev['src_mask'], outputs['src_mask'])
                            elif opt.sim_loss_update_one == 0:
                                aux_loss_dict = self.aux_loss_function(outputs_rev['context'].detach(), outputs['context'],
                                                                       outputs_rev['src_mask'], outputs['src_mask'])
                            elif opt.sim_loss_update_one == 1:
                                aux_loss_dict = self.aux_loss_function(outputs_rev['context'], outputs['context'].detach(),
                                                                       outputs_rev['src_mask'], outputs['src_mask'])
                            else:
                                raise NotImplementedError()
                            report_aux_loss += aux_loss_dict['data']
                            loss = aux_loss_dict['loss'].div(denom)  # a little trick to avoid gradient overflow with fp16

                            if self.cuda:
                                with amp.scale_loss(loss, optimizer) as scaled_loss:
                                    scaled_loss.backward()
                            else:
                                loss.backward()

                else:
                    # train classifier
                    # freeze enc & dec
                    self.model.encoder.requires_grad_(False)
                    self.model.decoder.requires_grad_(False)

                    if self.opt.language_classifier:
                        if self.opt.token_classifier == 0:  # language ID
                            targets_classifier = batch.get('targets_source_lang')
                        elif self.opt.token_classifier == 1:     # predict source token ID
                            targets_classifier = batch.get('source')
                        elif self.opt.token_classifier == 2:     # predict positional ID
                            targets_classifier = batch.get('source_pos')
                            targets_classifier[targets_classifier != 0] += 1  # start from 0
                            targets_classifier[0, :] += 1
                        elif self.opt.token_classifier == 3:     # predict POS tag
                            raise NotImplementedError

                        classifier_loss_dict = self.loss_function(outputs, targets=targets_classifier,
                                                                model=self.model, lan_classifier=True)
                        classifier_loss = classifier_loss_dict['loss'].div(
                            denom)  # a little trick to avoid gradient overflow with fp16
                        classifier_loss_data = classifier_loss_dict['data']
                        classifier_loss_data_rev = 0
                        # calc gradient for lan classifier
                        if self.cuda:
                            with amp.scale_loss(classifier_loss, optimizer) as scaled_loss:
                                scaled_loss.backward(retain_graph=self.opt.bidirectional_translation)
                        else:
                            classifier_loss.backward(retain_graph=self.opt.bidirectional_translation)

                        if self.opt.bidirectional_translation:
                            if opt.token_classifier == 0:
                                # predict language ID
                                targets_classifier = batch.get('targets_target_lang')  # starts from 1 (0 is padding)
                            elif opt.token_classifier == 1:
                                # predict source token ID
                                targets_classifier = batch.get('target')  # starts from 0 (padding), real tokens starts from 1
                            elif opt.token_classifier == 2:
                                # predict positional ID
                                targets_classifier = batch.get('target_pos')
                                targets_classifier[targets_classifier != 0] += 1  # start from 0
                                targets_classifier[0, :] += 1
                            else:
                                raise NotImplementedError

                            outputs_rev = self.model(batch, streaming=opt.streaming, target_mask=tgt_mask,
                                                    zero_encoder=opt.zero_encoder,
                                                    mirror=opt.mirror_loss, streaming_state=streaming_state,
                                                    reverse_src_tgt=True)

                            classifier_loss_dict = self.loss_function(outputs_rev, targets=targets_classifier,
                                                                    model=self.model, lan_classifier=True)
                            classifier_loss = classifier_loss_dict['loss'].div(
                                denom)  # a little trick to avoid gradient overflow with fp16
                            classifier_loss_data += classifier_loss_dict['data']
                            classifier_loss_data_rev += 0
                            # calc gradient for lan classifier
                            if self.cuda:
                                with amp.scale_loss(classifier_loss, optimizer) as scaled_loss:
                                    scaled_loss.backward()
                            else:
                                classifier_loss.backward()

                    if self.opt.gender_classifier:
                        # gender classifier
                        targets_classifier = batch.get('gen')
                        # print("(trainer.py) targets_classifier.size() gen: ", targets_classifier.size())

                        classifier_loss_dict = self.loss_function(outputs, targets=targets_classifier,
                                                                model=self.model, gen_classifier=True)
                        classifier_loss = classifier_loss_dict['loss'].div(
                            denom)  # a little trick to avoid gradient overflow with fp16
                        classifier_loss_data = classifier_loss_dict['data']
                        classifier_loss_data_rev = 0
                        # calc gradient for gender classifier
                        if self.cuda:
                            with amp.scale_loss(classifier_loss, optimizer) as scaled_loss:
                                scaled_loss.backward(retain_graph=self.opt.bidirectional_translation)
                        else:
                            classifier_loss.backward(retain_graph=self.opt.bidirectional_translation)

                        # if self.opt.bidirectional_translation:
                        #     # gender classifier
                        #     targets_classifier = batch.get('gen')

                            # outputs_rev = self.model(batch, streaming=opt.streaming, target_mask=tgt_mask,
                            #                         zero_encoder=opt.zero_encoder,
                            #                         mirror=opt.mirror_loss, streaming_state=streaming_state,
                            #                         reverse_src_tgt=True)

                    #     if self.opt.bidirectional_translation:
                    #         # gender classifier
                    #         targets_classifier = batch.get('gen')

                    #         outputs_rev = self.model(batch, streaming=opt.streaming, target_mask=tgt_mask,
                    #                                 zero_encoder=opt.zero_encoder,
                    #                                 mirror=opt.mirror_loss, streaming_state=streaming_state,
                    #                                 reverse_src_tgt=True)

                    #         classifier_loss_dict = self.loss_function(outputs_rev, targets=targets_classifier,
                    #                                                 model=self.model, gen_classifier=True)
                    #         classifier_loss = classifier_loss_dict['loss'].div(
                    #             denom)  # a little trick to avoid gradient overflow with fp16
                    #         classifier_loss_data += classifier_loss_dict['data']
                    #         classifier_loss_data_rev += 0
                    #         # calc gradient for lan classifier
                    #         if self.cuda:
                    #             with amp.scale_loss(classifier_loss, optimizer) as scaled_loss:
                    #                 scaled_loss.backward()
                    #         else:
                    #             classifier_loss.backward()

            except RuntimeError as e:
                if 'out of memory' in str(e):
                    print('| WARNING: ran out of memory on GPU , skipping batch')
                    oom = True
                    torch.cuda.empty_cache()
                    loss = 0
                    if opt.streaming:  # reset stream in this case ...
                        streaming_state = self.model.init_stream()
                else:
                    raise e

            if loss != loss:
                # catching NAN problem
                oom = True
                self.model.zero_grad()
                self.optim.zero_grad()
                num_accumulated_words = 0
                num_accumulated_sents = 0

            if not oom:
                if not self.opt.bidirectional_translation:
                    src_size = batch.src_size
                    tgt_size = batch.tgt_size
                else:
                    src_size = batch.src_size + batch.tgt_size
                    tgt_size = src_size

                counter = counter + 1
                num_accumulated_words += tgt_size
                num_accumulated_sents += batch_size

                #   We only update the parameters after getting gradients from n mini-batches
                update_flag = False
                if 0 < opt.batch_size_update <= num_accumulated_words: # use batch_size_update as indicator
                    update_flag = True
                elif counter >= opt.update_frequency and 0 >= opt.batch_size_update: # use update_frequency as indicator
                    update_flag = True
                elif i == n_samples - 1:  # update for the last minibatch
                    update_flag = True

                if update_flag:
                    grad_denom = 1 / denom
                    if self.opt.normalize_gradient:
                        grad_denom = num_accumulated_words / denom
                    normalize_gradients(amp.master_params(optimizer), grad_denom)
                    # Update the parameters.
                    if self.opt.max_grad_norm > 0:
                        torch.nn.utils.clip_grad_norm_(amp.master_params(optimizer), self.opt.max_grad_norm)
                    self.optim.step(grad_denom=grad_denom)
                    self.optim.zero_grad()
                    self.model.zero_grad()
                    counter = 0
                    num_accumulated_words = 0
                    num_accumulated_sents = 0
                    num_updates = self.optim._step

                    if opt.save_every > 0 and num_updates % opt.save_every == -1 % opt.save_every:
                        valid_loss, _ = self.eval(self.valid_data,
                                                  report_classifier=self.opt.token_classifier is not None,  # TODO lena token_classifier, gender?
                                                  report_cm=self.opt.token_classifier == 0,
                                                  bidirectional_translation=self.opt.bidirectional_translation)
                        valid_ppl = math.exp(min(valid_loss, 100))
                        print('Validation perplexity: %g' % valid_ppl)

                        ep = float(epoch) - 1. + ((float(i) + 1.) / n_samples)

                        self.save(ep, valid_ppl, itr=data_iterator)

                    update_counter += 1

                num_words = tgt_size
                report_loss += loss_data
                report_classifier_loss += classifier_loss_data if self.opt.language_classifier or self.opt.gender_classifier else 0
                report_classifier_loss_rev += classifier_loss_data_rev if self.opt.language_classifier or self.opt.gender_classifier else 0
                report_tgt_words += num_words
                report_src_words += src_size
                total_loss += loss_data
                total_words += num_words
                total_tokens += batch.get('target_output').nelement()
                total_non_pads += batch.get('target_output').ne(onmt.constants.PAD).sum().item()
                optim = self.optim
                batch_efficiency = total_non_pads / total_tokens

                if i == 0 or (i % opt.log_interval == -1 % opt.log_interval):
                    print(("Epoch %2d, %5d/%5d; ; ppl: %6.2f ; classifier loss: %6.2f ; classifier rev loss: %6.2f ; lr: %.7f ; num updates: %7d " +
                           "%5.0f src tok/s; %5.0f tgt tok/s; %s elapsed") %
                          (epoch, i + 1, len(data_iterator),
                           math.exp(report_loss / report_tgt_words),
                           report_classifier_loss / float(report_src_words),
                           report_classifier_loss_rev / float(report_src_words),
                           optim.getLearningRate(),
                           optim._step,
                           report_src_words / (time.time() - start),
                           report_tgt_words / (time.time() - start),
                           str(datetime.timedelta(seconds=int(time.time() - self.start_time)))))

                    if epoch >= self.opt.aux_loss_start_from:
                        print('********* Aux loss (after weight)', report_aux_loss / report_src_words)
                        print('********* Aux loss (original)', report_aux_loss / report_src_words / self.aux_loss_function.weight)

                    report_loss, report_tgt_words = 0, 0
                    report_classifier_loss = 0.0
                    report_src_words = 0
                    report_aux_loss = 0.0
                    start = time.time()

                i = i + 1

        return total_loss / total_words

    # def run(self, save_file=None):
    def run(self, checkpoint=None):

        opt = self.opt
        model = self.model
        optim = self.optim

        if checkpoint is not None:
            self.model.load_state_dict(checkpoint['model'])
            prec_opt = checkpoint['opt'] if 'opt' in checkpoint else None

            if not opt.reset_optim:
                print("* Loading optimizer states ... ")
                self.optim.load_state_dict(checkpoint['optim'])
                if prec_opt is not None and hasattr(prec_opt, "fp16_mixed"):
                    # Only load amp information if the mode is the same
                    # Maybe its better to change between optimization mode?
                    if opt.fp16_mixed == prec_opt.fp16_mixed and opt.fp16 == prec_opt.fp16:
                        if 'amp' in checkpoint:
                            amp.load_state_dict(checkpoint['amp'])

                # Only load the progress when we use the same optimizer
                if 'itr' in checkpoint:
                    itr_progress = checkpoint['itr']
                else:
                    itr_progress = None

                resume = True
                start_epoch = checkpoint['epoch'] if 'epoch' in checkpoint else 1
                if start_epoch is None:
                    start_epoch = 1

            else:
                itr_progress = None
                resume = False
                start_epoch = 1

            del checkpoint['model']
            del checkpoint['optim']
            del checkpoint
        else:
            itr_progress = None
            print('Initializing model parameters')
            init_model_parameters(model, opt)
            resume = False
            start_epoch = 1

        if opt.load_encoder_from:
            self.load_encoder_weight(opt.load_encoder_from)

        # if opt.load_decoder_from:
        #     self.load_decoder_weight(opt.load_decoder_from)

        report_classifier = opt.token_classifier is not None or opt.gender_classifier is not None
        report_confusion_matrix = opt.token_classifier == 0
        # if we are on a GPU: warm up the memory allocator
        if self.cuda:
            self.warm_up()
            print("(trainer.py): self.eval()")
            valid_loss, valid_adv_loss = self.eval(self.valid_data,
                                                   bidirectional_translation=self.opt.bidirectional_translation,
                                                   report_classifier=report_classifier,
                                                   report_cm=report_confusion_matrix)
            valid_ppl = math.exp(min(valid_loss, 100))
            print('Validation perplexity: %g, classifier loss: %6.6f' % (valid_ppl, valid_adv_loss))

        self.start_time = time.time()

        for epoch in range(opt.start_epoch, opt.start_epoch + opt.epochs):
            print('')

            #  (1) train for one epoch on the training set
            train_loss = self.train_epoch(epoch, resume=resume, itr_progress=itr_progress)
            train_ppl = math.exp(min(train_loss, 100))
            print('Train perplexity: %g' % train_ppl)

            #  (2) evaluate on the validation set
            valid_loss, valid_adv_loss = self.eval(self.valid_data,
                                                   bidirectional_translation=self.opt.bidirectional_translation,
                                                   report_classifier=report_classifier,
                                                   report_cm=report_confusion_matrix)
            valid_ppl = math.exp(min(valid_loss, 100))
            print('Validation perplexity: %g, adv loss: %6.6f' % (valid_ppl, valid_adv_loss))

            self.save(epoch, valid_ppl)
            itr_progress = None
            resume = False
