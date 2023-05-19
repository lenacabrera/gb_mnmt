from __future__ import division

import onmt
import onmt.markdown
import onmt.modules
import argparse
import torch
import time, datetime
from onmt.train_utils.trainer import XETrainer
from onmt.train_utils.trainer_zoo import XEAdversarialTrainer, XEGenderTrainer
from onmt.modules.loss import NMTLossFunc, NMTAndCTCLossFunc, MSEEncoderLoss, CosineEncoderLoss, CrossEntropyLossBase
from onmt.model_factory import build_model, optimize_model
from options import make_parser
from collections import defaultdict
import os
import numpy as np

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"

parser = argparse.ArgumentParser(description='train.py')
onmt.markdown.add_md_help_argument(parser)

# Please look at the options file to see the options regarding models and data
parser = make_parser(parser)

opt = parser.parse_args()

print(opt)

# An ugly hack to have weight norm on / off
onmt.constants.weight_norm = opt.weight_norm
onmt.constants.checkpointing = opt.checkpointing
onmt.constants.max_position_length = opt.max_position_length

# Use static dropout if checkpointing > 0
if opt.checkpointing > 0:
    onmt.constants.static = True

if torch.cuda.is_available() and not opt.gpus:
    print("WARNING: You have a CUDA device, should run with -gpus 0")

torch.manual_seed(opt.seed)


def numpy_to_torch(tensor_list):

    out_list = list()

    for tensor in tensor_list:
        if isinstance(tensor, np.ndarray):
            out_list.append(torch.from_numpy(tensor))
        else:
            out_list.append(tensor)

    return out_list


def main():

    if not opt.multi_dataset:
        if opt.data_format in ['bin', 'raw']:
            start = time.time()

            if opt.data.endswith(".train.pt"):
                print("Loading data from '%s'" % opt.data)
                dataset = torch.load(opt.data)
            else:
                print("Loading data from %s" % opt.data + ".train.pt")
                dataset = torch.load(opt.data + ".train.pt")

            elapse = str(datetime.timedelta(seconds=int(time.time() - start)))
            print("Done after %s" % elapse)

            dicts = dataset['dicts']

            # For backward compatibility
            train_dict = defaultdict(lambda: None, dataset['train'])
            valid_dict = defaultdict(lambda: None, dataset['valid'])

            if train_dict['src_lang'] is not None:
                assert 'langs' in dicts
                train_src_langs = train_dict['src_lang']
                train_tgt_langs = train_dict['tgt_lang']
            else:
                # allocate new languages
                dicts['langs'] = {'src': 0, 'tgt': 1}
                train_src_langs = list()
                train_tgt_langs = list()
                # Allocation one for the bilingual case
                train_src_langs.append(torch.Tensor([dicts['langs']['src']]))
                train_tgt_langs.append(torch.Tensor([dicts['langs']['tgt']]))

            if not opt.streaming:
                train_data = onmt.Dataset(train_dict['src'], train_dict['tgt'],
                                          src_sizes=None, tgt_sizes=None,
                                          src_langs=train_src_langs, tgt_langs=train_tgt_langs,
                                          batch_size_words=opt.batch_size_words,
                                          data_type=dataset.get("type", "text"), sorting=True,
                                          batch_size_sents=opt.batch_size_sents,
                                          multiplier=opt.batch_size_multiplier,
                                          augment=opt.augment_speech,
                                          upsampling=opt.upsampling,
                                          token_level_lang=opt.language_classifier_tok,
                                          num_split=len(opt.gpus),
                                          bidirectional=opt.bidirectional_translation,
                                          en_id=opt.en_id)
            else:
                train_data = onmt.StreamDataset(train_dict['src'], train_dict['tgt'],
                                                src_sizes=None, tgt_sizes=None,
                                                src_langs=train_src_langs, tgt_langs=train_tgt_langs,
                                                batch_size_words=opt.batch_size_words,
                                                data_type=dataset.get("type", "text"), sorting=True,
                                                batch_size_sents=opt.batch_size_sents,
                                                multiplier=opt.batch_size_multiplier,
                                                augment=opt.augment_speech,
                                                upsampling=opt.upsampling,
                                                en_id=opt.en_id)

            if valid_dict['src_lang'] is not None:
                assert 'langs' in dicts
                valid_src_langs = valid_dict['src_lang']
                valid_tgt_langs = valid_dict['tgt_lang']
            else:
                # allocate new languages
                valid_src_langs = list()
                valid_tgt_langs = list()

                # Allocation one for the bilingual case
                valid_src_langs.append(torch.Tensor([dicts['langs']['src']]))
                valid_tgt_langs.append(torch.Tensor([dicts['langs']['tgt']]))

            if not opt.streaming:
                valid_data = onmt.Dataset(valid_dict['src'], valid_dict['tgt'],
                                          src_sizes=None, tgt_sizes=None,
                                          src_langs=valid_src_langs, tgt_langs=valid_tgt_langs,
                                          batch_size_words=opt.batch_size_words,
                                          data_type=dataset.get("type", "text"), sorting=True,
                                          batch_size_sents=opt.batch_size_sents,
                                          upsampling=opt.upsampling,
                                          token_level_lang=opt.language_classifier_tok,
                                          bidirectional=opt.bidirectional_translation,
                                          en_id=opt.en_id)
            else:
                valid_data = onmt.StreamDataset(valid_dict['src'], valid_dict['tgt'],
                                                src_sizes=None, tgt_sizes=None,
                                                src_langs=valid_src_langs, tgt_langs=valid_tgt_langs,
                                                batch_size_words=opt.batch_size_words,
                                                data_type=dataset.get("type", "text"), sorting=True,
                                                batch_size_sents=opt.batch_size_sents,
                                                upsampling=opt.upsampling)

            print(' * number of training sentences. %d' % len(dataset['train']['src']))
            print(' * maximum batch size (words per batch). %d' % opt.batch_size_words)

        elif opt.data_format in ['scp', 'scpmem', 'mmem']:
            print("Loading memory mapped data files ....")
            start = time.time()
            from onmt.data.mmap_indexed_dataset import MMapIndexedDataset
            from onmt.data.scp_dataset import SCPIndexDataset

            dicts = torch.load(opt.data + ".dict.pt")
            if opt.data_format in ['scp', 'scpmem']:
                audio_data = torch.load(opt.data + ".scp_path.pt")

            # allocate languages if not
            if 'langs' not in dicts:
                dicts['langs'] = {'src': 0, 'tgt': 1}
            else:
                print(dicts['langs'])

            train_path = opt.data + '.train'
            if opt.data_format in ['scp', 'scpmem']:
                train_src = SCPIndexDataset(audio_data['train'], concat=opt.concat)
            else:
                train_src = MMapIndexedDataset(train_path + '.src')

            train_tgt = MMapIndexedDataset(train_path + '.tgt')

            # check the lang files if they exist (in the case of multi-lingual models)
            if os.path.exists(train_path + '.src_lang.bin'):
                assert 'langs' in dicts
                train_src_langs = MMapIndexedDataset(train_path + '.src_lang')
                train_tgt_langs = MMapIndexedDataset(train_path + '.tgt_lang')
            else:
                train_src_langs = list()
                train_tgt_langs = list()
                # Allocate a Tensor(1) for the bilingual case
                train_src_langs.append(torch.Tensor([dicts['langs']['src']]))
                train_tgt_langs.append(torch.Tensor([dicts['langs']['tgt']]))


            # check if gender files exist (in the case of mushe training data)
            if os.path.exists(train_path + '.gen_sent.bin'):
                assert 'gen_sent' in dicts
                train_gen_sent = MMapIndexedDataset(train_path + '.gen_sent')
            else:
                train_gen_sent = list()

            # check if gender files exist (in the case of mushe training data)
            if os.path.exists(train_path + '.gen_tok.bin'):
                assert 'gen_tok' in dicts
                train_gen_tok = MMapIndexedDataset(train_path + '.gen_tok')
            else:
                train_gen_tok = list()


            # check the length files if they exist
            if os.path.exists(train_path + '.src_sizes.npy'):
                train_src_sizes = np.load(train_path + '.src_sizes.npy')
                train_tgt_sizes = np.load(train_path + '.tgt_sizes.npy')
            else:
                train_src_sizes, train_tgt_sizes = None, None

            if opt.encoder_type == 'audio':
                data_type = 'audio'
            else:
                data_type = 'text'

            if not opt.streaming:
                if opt.gender_classifier:
                    if opt.gender_classifier_tok:
                        train_gen_data = train_gen_tok
                    elif opt.gender_classifier_sent:
                        train_gen_data = train_gen_sent
                    else:
                        raise NotImplementedError
                else:
                    train_gen_data = None

                train_data = onmt.Dataset(train_src,
                                          train_tgt,
                                          train_src_sizes, train_tgt_sizes,
                                          train_src_langs, train_tgt_langs,
                                          train_gen_data,
                                          batch_size_words=opt.batch_size_words,
                                          data_type=data_type, sorting=True,
                                          batch_size_sents=opt.batch_size_sents,
                                          multiplier=opt.batch_size_multiplier,
                                          src_align_right=opt.src_align_right,
                                          augment=opt.augment_speech,
                                          upsampling=opt.upsampling,
                                          cleaning=True, verbose=True,
                                          num_split=len(opt.gpus),
                                          token_level_lang=opt.language_classifier_tok,
                                          token_level_gen=opt.gender_classifier_tok,
                                          bidirectional=opt.bidirectional_translation,
                                          en_id=opt.en_id)
            else:
                train_data = onmt.StreamDataset(train_src,
                                                train_tgt,
                                                train_src_langs, train_tgt_langs,
                                                batch_size_words=opt.batch_size_words,
                                                data_type=data_type, sorting=False,
                                                batch_size_sents=opt.batch_size_sents,
                                                multiplier=opt.batch_size_multiplier,
                                                upsampling=opt.upsampling)

            valid_path = opt.data + '.valid'
            if opt.data_format in ['scp', 'scpmem']:
                valid_src = SCPIndexDataset(audio_data['valid'], concat=opt.concat)
            else:
                valid_src = MMapIndexedDataset(valid_path + '.src')
            valid_tgt = MMapIndexedDataset(valid_path + '.tgt')

            if os.path.exists(valid_path + '.src_lang.bin'):
                assert 'langs' in dicts
                valid_src_langs = MMapIndexedDataset(valid_path + '.src_lang')
                valid_tgt_langs = MMapIndexedDataset(valid_path + '.tgt_lang')
            else:
                valid_src_langs = list()
                valid_tgt_langs = list()

                # Allocation one for the bilingual case
                valid_src_langs.append(torch.Tensor([dicts['langs']['src']]))
                valid_tgt_langs.append(torch.Tensor([dicts['langs']['tgt']]))


            # check if gender files exist (in the case of mushe training data)
            if os.path.exists(valid_path + '.gen_sent.bin'):
                assert 'gen_sent' in dicts
                valid_gen_sent = MMapIndexedDataset(valid_path + '.gen_sent')
            else:
                valid_gen_sent = list()

            # check if gender files exist (in the case of mushe training data)
            if os.path.exists(valid_path + '.gen_tok.bin'):
                assert 'gen_tok' in dicts
                valid_gen_tok = MMapIndexedDataset(valid_path + '.gen_tok')
            else:
                valid_gen_tok = list()


            # check the length files if they exist
            if os.path.exists(valid_path + '.src_sizes.npy'):
                valid_src_sizes = np.load(valid_path + '.src_sizes.npy')
                valid_tgt_sizes = np.load(valid_path + '.tgt_sizes.npy')
            else:
                valid_src_sizes, valid_tgt_sizes = None, None

            if not opt.streaming:
                if opt.gender_classifier:
                    if opt.gender_classifier_tok:
                        valid_gen_data = valid_gen_tok
                    elif opt.gender_classifier_sent:
                        valid_gen_data = valid_gen_sent
                    else:
                        raise NotImplementedError
                else:
                    valid_gen_data = None
                valid_data = onmt.Dataset(valid_src, valid_tgt,
                                          valid_src_sizes, valid_tgt_sizes,
                                          valid_src_langs, valid_tgt_langs,
                                          valid_gen_data,
                                          batch_size_words=opt.batch_size_words,
                                          data_type=data_type, sorting=True,
                                          batch_size_sents=opt.batch_size_sents,
                                          src_align_right=opt.src_align_right,
                                          cleaning=True, verbose=True, debug=True,
                                          num_split=len(opt.gpus),
                                          token_level_lang=opt.language_classifier_tok,
                                          token_level_gen=opt.gender_classifier_tok,
                                          bidirectional=opt.bidirectional_translation,
                                          en_id=opt.en_id)
            else:
                # for validation data, we have to go through sentences (very slow but to ensure correctness)
                valid_data = onmt.StreamDataset(valid_src, valid_tgt,
                                                valid_src_langs, valid_tgt_langs,
                                                batch_size_words=opt.batch_size_words,
                                                data_type=data_type, sorting=True,
                                                batch_size_sents=opt.batch_size_sents)

            elapse = str(datetime.timedelta(seconds=int(time.time() - start)))
            print("Done after %s" % elapse)

        else:
            raise NotImplementedError

        print(' * number of sentences in training data: %d' % train_data.size())
        print(' * number of sentences in validation data: %d' % valid_data.size())

    else:
        print("[INFO] Reading multiple dataset ...")
        # raise NotImplementedError

        dicts = torch.load(opt.data + ".dict.pt")

        root_dir = os.path.dirname(opt.data)
        print(dicts['langs'])
        print("Loading training data ...")

        train_dirs, valid_dirs = dict(), dict()

        # scan the data directory to find the training data
        for dir_ in os.listdir(root_dir):
            if os.path.isdir(os.path.join(root_dir, dir_)):
                if str(dir_).startswith("train"):
                    idx = int(dir_.split(".")[1])
                    train_dirs[idx] = dir_
                if dir_.startswith("valid"):
                    idx = int(dir_.split(".")[1])
                    valid_dirs[idx] = dir_

        train_sets, valid_sets = list(), list()

        for (idx_, dir_) in sorted(train_dirs.items()):

            data_dir = os.path.join(root_dir, dir_)
            print("[INFO] Loading training data %i from %s" % (idx_, dir_))

            if opt.data_format in ['bin', 'raw']:
                raise NotImplementedError

            elif opt.data_format in ['scp', 'scpmem', 'mmem']:
                from onmt.data.mmap_indexed_dataset import MMapIndexedDataset
                from onmt.data.scp_dataset import SCPIndexDataset

                if opt.data_format in ['scp', 'scpmem']:
                    audio_data = torch.load(os.path.join(data_dir, "data.scp_path.pt"))
                    src_data = SCPIndexDataset(audio_data, concat=opt.concat)
                else:
                    src_data = MMapIndexedDataset(os.path.join(data_dir, "data.src"))

                tgt_data = MMapIndexedDataset(os.path.join(data_dir, "data.tgt"))

                src_lang_data = MMapIndexedDataset(os.path.join(data_dir, 'data.src_lang'))
                tgt_lang_data = MMapIndexedDataset(os.path.join(data_dir, 'data.tgt_lang'))

                if os.path.exists(os.path.join(data_dir, 'data.src_sizes.npy')):
                    src_sizes = np.load(os.path.join(data_dir, 'data.src_sizes.npy'))
                    tgt_sizes = np.load(os.path.join(data_dir, 'data.tgt_sizes.npy'))
                else:
                    src_sizes, sizes = None, None

                if opt.encoder_type == 'audio':
                    data_type = 'audio'
                else:
                    data_type = 'text'

                if not opt.streaming:
                    train_data = onmt.Dataset(src_data,
                                              tgt_data,
                                              src_sizes, tgt_sizes,
                                              src_lang_data, tgt_lang_data,
                                              batch_size_words=opt.batch_size_words,
                                              data_type=data_type, sorting=True,
                                              batch_size_sents=opt.batch_size_sents,
                                              multiplier=opt.batch_size_multiplier,
                                              src_align_right=opt.src_align_right,
                                              augment=opt.augment_speech,
                                              upsampling=opt.upsampling,
                                              cleaning=True, verbose=True,
                                              num_split=len(opt.gpus),
                                              token_level_lang=opt.language_classifier_tok,
                                              bidirectional=opt.bidirectional_translation,
                                              multidataset=True,
                                              en_id=opt.en_id)

                    train_sets.append(train_data)

                else:
                    print("Multi-dataset not implemented for Streaming tasks.")
                    raise NotImplementedError

        for (idx_, dir_) in sorted(valid_dirs.items()):

            data_dir = os.path.join(root_dir, dir_)

            print("[INFO] Loading validation data %i from %s" % (idx_, dir_))

            if opt.data_format in ['bin', 'raw']:
                raise NotImplementedError

            elif opt.data_format in ['scp', 'scpmem', 'mmem']:

                if opt.data_format in ['scp', 'scpmem']:
                    audio_data = torch.load(os.path.join(data_dir, "data.scp_path.pt"))
                    src_data = SCPIndexDataset(audio_data, concat=opt.concat)
                else:
                    src_data = MMapIndexedDataset(os.path.join(data_dir, "data.src"))

                tgt_data = MMapIndexedDataset(os.path.join(data_dir, "data.tgt"))

                src_lang_data = MMapIndexedDataset(os.path.join(data_dir, 'data.src_lang'))
                tgt_lang_data = MMapIndexedDataset(os.path.join(data_dir, 'data.tgt_lang'))

                if os.path.exists(os.path.join(data_dir, 'data.src_sizes.npy')):
                    src_sizes = np.load(os.path.join(data_dir, 'data.src_sizes.npy'))
                    tgt_sizes = np.load(os.path.join(data_dir, 'data.tgt_sizes.npy'))
                else:
                    src_sizes, sizes = None, None

                if opt.encoder_type == 'audio':
                    data_type = 'audio'
                else:
                    data_type = 'text'

                if not opt.streaming:
                    valid_data = onmt.Dataset(src_data, tgt_data,
                                              src_sizes, tgt_sizes,
                                              src_lang_data, tgt_lang_data,
                                              batch_size_words=opt.batch_size_words,
                                              data_type=data_type, sorting=True,
                                              batch_size_sents=opt.batch_size_sents,
                                              src_align_right=opt.src_align_right,
                                              cleaning=True, verbose=True, debug=True,
                                              num_split=len(opt.gpus),
                                              token_level_lang=opt.language_classifier_tok,
                                              bidirectional=opt.bidirectional_translation,
                                              multidataset=True,
                                              en_id=opt.en_id)

                    valid_sets.append(valid_data)

                else:
                    raise NotImplementedError

        train_data = train_sets
        valid_data = valid_sets

    if opt.load_from:
        checkpoint = torch.load(opt.load_from, map_location=lambda storage, loc: storage)
        print("* Loading dictionaries from the checkpoint")
        dicts = checkpoint['dicts']
        print("(train.py) dict.keys() of checkpoint/saved model: ", dicts.keys())

        if opt.load_vocab_from_data is not None:  # only useful when vocab is expanded
            vocab_data = torch.load(opt.load_vocab_from_data, map_location=lambda storage, loc: storage)
            print(vocab_data.keys())
            # TODO: OVERWRITE src and tgt?
            dicts['src'] = vocab_data['src']
            dicts['tgt'] = vocab_data['tgt']
            # for tok in vocab_data['dicts']['src'].labelToIdx:  # toks in new language
            #     dicts['src'].add(tok)
            # for tok in vocab_data['dicts']['tgt'].labelToIdx:  # toks new language
            #     dicts['tgt'].add(tok)

            # TODO: doesn't really hurt supervised directions when re-initializing this?
             # if len(vocab_data['dicts']['langs']) > dicts['langs']:
            for lan in vocab_data['langs']:  # new language
                if lan not in dicts['langs']:
                    dicts['langs'][lan] = len(dicts['langs'])
                    print(' *** added language dict {0} to {1}'.format(lan, dicts['langs']))
            # else::q
            # dicts['langs'] = vocab_data['dicts']['langs']

            # print(dicts['langs']['cs'])
            # print(vocab_data['gen'])
            # if 'gen' not in dicts:
            #     dicts['gen'] = list()
            # for lan in vocab_data['gen']:
            #     print(lan)
            #     if lan not in dicts['gen']:
            #         dicts['gen'][lan] = len(dicts['gen'])
            #         print(' *** added gender dict {0} to {1}'.format(gen, dicts['gen']))

    else:
        dicts['tgt'].patch(opt.patch_vocab_multiplier)
        checkpoint = None

    if "src" in dicts:
        print(' * vocabulary size. source = %d; target = %d' %
              (dicts['src'].size(), dicts['tgt'].size()))
    else:
        print(' * vocabulary size. target = %d' %
              (dicts['tgt'].size()))

    print('* Building model...')

    if not opt.fusion:
        model = build_model(opt, dicts)

        """ Building the loss function """

        if opt.ctc_loss > 0.0:
            from onmt.speech.ctc_loss import CTC
            loss_function = CTC(dicts['tgt'].size(), opt.model_size, 0.0, reduce=True)
        # if opt.ctc_loss != 0:
        #     loss_function = NMTAndCTCLossFunc(dicts['tgt'].size(),
        #                                       label_smoothing=opt.label_smoothing,
        #                                       ctc_weight=opt.ctc_loss)
        else:
            loss_function = NMTLossFunc(opt.model_size, dicts['tgt'].size(),
                                        label_smoothing=opt.label_smoothing,
                                        mirror=opt.mirror_loss)

        # This function replaces modules with the more optimized counterparts so that it can run faster
        # Currently exp with LayerNorm
        optimize_model(model)

    else:
        from onmt.model_factory import build_fusion
        from onmt.modules.loss import FusionLoss

        model = build_fusion(opt, dicts)

        loss_function = FusionLoss(dicts['tgt'].size(), label_smoothing=opt.label_smoothing)

    if opt.sim_loss_type:
        sim_loss_input_type = opt.sim_loss_type % 10
        sim_loss_func_type = opt.sim_loss_type // 10
        aux_loss_weight = opt.aux_loss_weight

        if sim_loss_func_type == 1:
            aux_loss_function = MSEEncoderLoss(input_type=sim_loss_input_type, weight=aux_loss_weight)
        elif sim_loss_func_type == 2:
            aux_loss_function = CosineEncoderLoss(input_type=sim_loss_input_type, weight=aux_loss_weight)
        else:
            raise NotImplementedError

    else:
        aux_loss_function = None

    n_params = sum([p.nelement() for p in model.parameters()])
    print('* number of parameters: %d' % n_params)

    if len(opt.gpus) > 1 or opt.virtual_gpu > 1:
        raise NotImplementedError("Multi-GPU training is not supported at the moment.")
    else:
        if not opt.adversarial_classifier:
            trainer = XETrainer(model, loss_function, train_data, valid_data, dicts, opt, True, aux_loss_function)
        else:
            trainer = XEAdversarialTrainer(model, loss_function, train_data, valid_data, dicts, opt)

    trainer.run(checkpoint=checkpoint)


if __name__ == "__main__":
    main()

