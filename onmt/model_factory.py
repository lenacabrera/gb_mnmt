import torch
import torch.nn as nn
import onmt
from onmt.models.transformers import TransformerEncoder, TransformerDecoder, Transformer, MixedEncoder, MultiSourceEncoder, DoubleTransformer
from onmt.models.transformer_layers import PositionalEncoding
from onmt.models.relative_transformer import SinusoidalPositionalEmbedding, RelativeTransformer
from onmt.modules.copy_generator import CopyGenerator
from options import backward_compatible
import math

init = torch.nn.init

MAX_LEN = onmt.constants.max_position_length  # This should be the longest sentence from the dataset


def build_model(opt, dicts):
    opt = backward_compatible(opt)

    onmt.constants.layer_norm = opt.layer_norm
    onmt.constants.weight_norm = opt.weight_norm
    onmt.constants.activation_layer = opt.activation_layer
    onmt.constants.version = 1.0
    onmt.constants.attention_out = opt.attention_out
    onmt.constants.residual_type = opt.residual_type

    if not opt.fusion:
        model = build_tm_model(opt, dicts)
    else:
        raise NotImplementedError
        model = build_fusion(opt, dicts)

    return model


def build_tm_model(opt, dicts):
    # BUILD POSITIONAL ENCODING
    if opt.time == 'positional_encoding':
        positional_encoder = PositionalEncoding(opt.model_size, len_max=MAX_LEN,
                                                fixed_encoding=not opt.learnable_position_encoding)
    else:
        raise NotImplementedError

    # BUILD GENERATOR
    if opt.copy_generator:
        generators = [CopyGenerator(opt.model_size, dicts['tgt'].size(),
                                    fix_norm=opt.fix_norm_output_embedding)]
    else:
        generators = [onmt.modules.base_seq2seq.Generator(opt.model_size, dicts['tgt'].size(),
                                                          fix_norm=opt.fix_norm_output_embedding)]

    # build classifier
    # (1) language
    if opt.language_classifier:
        mid_layer_size = opt.language_classifer_mid_layer_size

        if opt.token_classifier is not None:
            if opt.token_classifier == 0:
                # predict source language ID
                output_size = opt.num_classifier_languages
            elif opt.token_classifier == 1:
                # predict source token ID
                output_size = len(dicts['src'].idxToLabel)
            elif opt.token_classifier == 2:
                # predict positional ID
                output_size = opt.max_position_length
            else:
                raise NotImplementedError
        else:
            output_size = opt.num_classifier_languages
            opt.token_classifier = 0

        if opt.token_classifier_at is not None and opt.token_classifier_at != -1:
            classifier_input_name = 'mid_layer_output'  # specified encoder layer
        else:
            classifier_input_name = 'context'   # encoder output

        generators.append(onmt.modules.base_seq2seq.Classifier(hidden_size=opt.model_size,
                                                               output_size=output_size,  # padding is 0
                                                               fix_norm=False, grad_scale=opt.gradient_scale,
                                                               mid_layer_size=mid_layer_size,
                                                               input_name=classifier_input_name))

    # (2) gender
    if opt.gender_classifier:
        gender_mid_layer_size = opt.gender_mid_layer_size

        if opt.gender_classifier_sent:
            gender_output_size = 2
        elif opt.gender_classifier_tok:
            gender_output_size = 3
        else:
            raise NotImplementedError
        print("(model_factory.py) gender_output_size/num labels: ", gender_output_size)

        if opt.gender_token_classifier_at is not None and opt.gender_token_classifier_at != -1:
            gender_classifier_input_name = 'mid_layer_output'  # specified encoder layer
        else:
            if opt.gender_classifier_sent:
                gender_classifier_input_name = 'context_avgpool'
            else:
                gender_classifier_input_name = 'context'   # encoder output

        generators.append(onmt.modules.base_seq2seq.Classifier(hidden_size=opt.model_size,
                                                               output_size=gender_output_size,  # padding is 0
                                                               fix_norm=False, grad_scale=opt.gradient_scale,
                                                               mid_layer_size=gender_mid_layer_size,
                                                               input_name=gender_classifier_input_name))

    # BUILD EMBEDDINGS
    if 'src' in dicts:
        embedding_src = nn.Embedding(dicts['src'].size(),
                                     opt.model_size,
                                     padding_idx=onmt.constants.PAD)
    else:
        embedding_src = None

    if opt.join_embedding and embedding_src is not None:
        embedding_tgt = embedding_src
        print("* Joining the weights of encoder and decoder word embeddings")
    else:
        embedding_tgt = nn.Embedding(dicts['tgt'].size(),
                                     opt.model_size,
                                     padding_idx=onmt.constants.PAD)

    if opt.use_language_embedding:
        print("* Create language embeddings with %d languages" % len(dicts['langs']))
        language_embeddings = nn.Embedding(len(dicts['langs']), opt.model_size)
        opt.n_languages = len(dicts['langs'])
    else:
        language_embeddings = None

    if 0 < opt.ctc_loss < 1.0:  # TODO: was "!= 0:"
        generators.append(onmt.modules.base_seq2seq.Generator(opt.model_size, dicts['tgt'].size() + 1))

    if opt.model in ['transformer', 'stochastic_transformer']:
        onmt.constants.init_value = opt.param_init

        if opt.encoder_type == "text":
            encoder = TransformerEncoder(opt, embedding_src, positional_encoder,
                                         opt.encoder_type, language_embeddings=language_embeddings)
        elif opt.encoder_type == "audio":
            encoder = TransformerEncoder(opt, None, positional_encoder, opt.encoder_type)
        elif opt.encoder_type == "mix":
            text_encoder = TransformerEncoder(opt, embedding_src, positional_encoder,
                                              "text", language_embeddings=language_embeddings)
            audio_encoder = TransformerEncoder(opt, None, positional_encoder, "audio")
            encoder = MixedEncoder(text_encoder, audio_encoder)
        else:
            print("Unknown encoder type:", opt.encoder_type)
            exit(-1)

        decoder = TransformerDecoder(opt, embedding_tgt, positional_encoder, language_embeddings=language_embeddings)

        model = Transformer(encoder, decoder, nn.ModuleList(generators), mirror=opt.mirror_loss, ctc=opt.ctc_loss)

    elif opt.model == 'multi_source_target_transformer':
        print('*** Multi source-target encoder')

        if opt.encoder_type == "text":
            encoder_main = TransformerEncoder(opt, embedding_src, positional_encoder, opt.encoder_type,
                                              language_embeddings=language_embeddings)
            encoder_aux = encoder_main
            encoder = MultiSourceEncoder(opt, embedding_src, encoder_main, encoder_aux)

            decoder_main = TransformerDecoder(opt, embedding_tgt, positional_encoder,
                                              language_embeddings=language_embeddings)
            decoder_aux = decoder_main
            # decoder = MultiSourceDecoder(opt, decoder_main, decoder_aux, embedding_tgt, positional_encoder)

        else:
            raise NotImplementedError('Not implemented')

        model = DoubleTransformer(encoder, decoder_main, decoder_aux, nn.ModuleList(generators), mirror=opt.mirror_loss)

    elif opt.model == 'relative_transformer':

        from onmt.models.relative_transformer import RelativeTransformerEncoder, RelativeTransformerDecoder, \
            RelativeTransformer

        if opt.encoder_type == "text":
            encoder = RelativeTransformerEncoder(opt, embedding_src, None,
                                                 opt.encoder_type, language_embeddings=language_embeddings)
        if opt.encoder_type == "audio":
            # raise NotImplementedError
            encoder = RelativeTransformerEncoder(opt, None, None, encoder_type=opt.encoder_type,
                                                 language_embeddings=language_embeddings)

        generator = nn.ModuleList(generators)
        decoder = RelativeTransformerDecoder(opt, embedding_tgt, None, language_embeddings=language_embeddings)
        model = RelativeTransformer(encoder, decoder, generator, mirror=opt.mirror_loss)

    elif opt.model == 'distance_transformer':

        from onmt.models.relative_transformer import RelativeTransformerDecoder, RelativeTransformer
        from onmt.models.distance_transformer import DistanceTransformerEncoder

        if opt.encoder_type == "text":
            encoder = DistanceTransformerEncoder(opt, embedding_src, None,
                                                 opt.encoder_type, language_embeddings=language_embeddings)
        if opt.encoder_type == "audio":
            # raise NotImplementedError
            encoder = DistanceTransformerEncoder(opt, None, None, encoder_type=opt.encoder_type,
                                                 language_embeddings=language_embeddings)

        generator = nn.ModuleList(generators)
        decoder = RelativeTransformerDecoder(opt, embedding_tgt, None, language_embeddings=language_embeddings)
        model = RelativeTransformer(encoder, decoder, generator, mirror=opt.mirror_loss)

    elif opt.model == 'unified_transformer':
        from onmt.models.unified_transformer import UnifiedTransformer

        if opt.encoder_type == "audio":
            raise NotImplementedError

        generator = nn.ModuleList(generators)
        model = UnifiedTransformer(opt, embedding_src, embedding_tgt,
                                   generator, positional_encoder, language_embeddings=language_embeddings)

    elif opt.model == 'relative_unified_transformer':
        from onmt.models.relative_unified_transformer import RelativeUnifiedTransformer

        if opt.encoder_type == "audio":
            raise NotImplementedError

        generator = nn.ModuleList(generators)
        model = RelativeUnifiedTransformer(opt, embedding_src, embedding_tgt,
                                           generator, positional_encoder, language_embeddings=language_embeddings)

    elif opt.model == 'memory_transformer':
        from onmt.models.memory_transformer import MemoryTransformer

        if opt.encoder_type == "audio":
            raise NotImplementedError

        generator = nn.ModuleList(generators)
        model = MemoryTransformer(opt, embedding_src, embedding_tgt,
                                  generator, positional_encoder, language_embeddings=language_embeddings,
                                  dictionary=dicts['tgt'])

    else:
        raise NotImplementedError

    if opt.tie_weights:
        print("* Joining the weights of decoder input and output embeddings")
        model.tie_weights()

    return model


def init_model_parameters(model, opt):
    """
    Initializing model parameters. Mostly using normal distribution (0, std)
    """
    init_std = 0.02  # magical number

    def init_weight(weight):
        if len(weight.shape) == 2:
            std_ = math.sqrt(2.0 / (weight.shape[0] + weight.shape[1]))
            nn.init.normal_(weight, 0.0, std_)
        else:
            nn.init.normal_(weight, 0.0, init_std)

    def init_embed(weight):
        # nn.init.uniform_(weight, -0.01, 0.01)
        nn.init.normal_(weight, 0.0, 0.02)

    def init_bias(bias):
        # nn.init.constant_(bias, 0.0)
        nn.init.normal_(bias, 0.0, init_std)

    def weights_init(m):
        classname = m.__class__.__name__
        if classname.find('Linear') != -1:
            if hasattr(m, 'weight') and m.weight is not None:
                init_weight(m.weight)
            if hasattr(m, 'bias') and m.bias is not None:
                init_bias(m.bias)
        elif classname.find('Embedding') != -1:

            initialize = True
            if hasattr(m, "no_need_to_initialize"):
                if m.no_need_to_initialize:
                    initialize = False
            if initialize:
                if opt.init_embedding == 'normal':
                    if hasattr(m, 'weight'):
                        init_weight(m.weight)
                elif opt.init_embedding in ['uniform', 'xavier']:
                    if hasattr(m, 'weight'):
                        init_embed(m.weight)
        elif classname.find('LayerNorm') != -1 or classname.find('FusedLayerNorm') != -1:
            if hasattr(m, 'weight'):
                nn.init.normal_(m.weight, 1.0, init_std)
            if hasattr(m, 'bias') and m.bias is not None:
                init_bias(m.bias)
        elif classname.find('RelativeTransformerEncoder') != -1:
            if hasattr(m, 'r_emb'):
                init_weight(m.r_emb)
            if hasattr(m, 'r_w_bias'):
                init_weight(m.r_w_bias)
            if hasattr(m, 'r_r_bias'):
                init_weight(m.r_r_bias)
            if hasattr(m, 'r_bias'):
                init_bias(m.r_bias)
        elif classname.find('RelativeTransformerDecoder') != -1:
            if hasattr(m, 'r_emb'):
                init_weight(m.r_emb)
            if hasattr(m, 'r_w_bias'):
                init_weight(m.r_w_bias)
            if hasattr(m, 'r_r_bias'):
                init_weight(m.r_r_bias)
            if hasattr(m, 'r_bias'):
                init_bias(m.r_bias)
        elif classname.find('RelPartialLearnableMultiHeadAttn') != -1:
            if hasattr(m, 'r_w_bias'):
                init_weight(m.r_w_bias)
            if hasattr(m, 'r_r_bias'):
                init_weight(m.r_r_bias)

    model.apply(weights_init)

    if hasattr(model, 'decoder'):
        model.decoder.word_lut.apply(weights_init)
    else:
        model.tgt_embedding.apply(weights_init)

    return


def build_language_model(opt, dicts):
    opt = backward_compatible(opt)

    onmt.constants.layer_norm = opt.layer_norm
    onmt.constants.weight_norm = opt.weight_norm
    onmt.constants.activation_layer = opt.activation_layer
    onmt.constants.version = 1.0
    onmt.constants.attention_out = opt.attention_out
    onmt.constants.residual_type = opt.residual_type

    from onmt.models.transformer_xl import TransformerXL

    embedding_tgt = nn.Embedding(dicts['tgt'].size(),
                                 opt.model_size,
                                 padding_idx=onmt.constants.PAD)
    if opt.use_language_embedding:
        print("* Create language embeddings with %d languages" % len(dicts['langs']))
        language_embeddings = nn.Embedding(len(dicts['langs']), opt.model_size)
    else:
        language_embeddings = None

    generators = [onmt.modules.base_seq2seq.Generator(opt.model_size, dicts['tgt'].size())]

    model = TransformerXL(opt, embedding_tgt, nn.ModuleList(generators), language_embeddings=language_embeddings)

    model.tgt_dict = dicts['tgt']

    if opt.tie_weights:
        print("* Joining the weights of decoder input and output embeddings")
        model.tie_weights()

    return model


def build_fusion(opt, dicts):
    # the fusion model requires a pretrained language model
    print("Loading pre-trained language model from %s" % opt.lm_checkpoint)
    lm_checkpoint = torch.load(opt.lm_checkpoint, map_location=lambda storage, loc: storage)

    # first we build the lm model and lm checkpoint
    lm_opt = lm_checkpoint['opt']

    lm_model = build_language_model(lm_opt, dicts)

    # load parameter for pretrained model
    lm_model.load_state_dict(lm_checkpoint['model'])

    # main model for seq2seq (translation, asr)
    tm_model = build_tm_model(opt, dicts)

    from onmt.legacy.FusionNetwork.Models import FusionNetwork
    model = FusionNetwork(tm_model, lm_model)

    return model


def optimize_model(model, fp16=True, distributed=False):
    """
    Used to potentially upgrade the components with more optimized counterparts in the future
    """

    def replace_layer_norm(m, name):

        replacable = True
        try:
            # from apex.normalization.fused_layer_norm import FusedLayerNorm
            import importlib
            from apex.normalization.fused_layer_norm import FusedLayerNorm
            fused_layer_norm_cuda = importlib.import_module("fused_layer_norm_cuda")

        except ModuleNotFoundError:
            replacable = False

        # if replacable:
        #     for attr_str in dir(m):
        #         target_attr = getattr(m, attr_str)
        #         if type(target_attr) == torch.nn.LayerNorm:
        #             setattr(m, attr_str, FusedLayerNorm(target_attr.normalized_shape,
        #                                                 eps=target_attr.eps,
        #                                                 elementwise_affine=target_attr.elementwise_affine))
        #     for n, ch in m.named_children():
        #         replace_layer_norm(ch, n)

        def safe_batch_norm(m, name):
            for attr_str in dir(m):
                target_attr = getattr(m, attr_str)
                if type(target_attr) == torch.nn.BatchNorm2d or type(target_attr) == torch.nn.BatchNorm1d:

                    if fp16:
                        target_attr.eps = 1e-5  # tiny value for fp16 according to AllenNLP

                    setattr(m, attr_str, target_attr)

    replace_layer_norm(model, "Transformer")

    # if fp16:
    #     safe_batch_norm(model, "Transformer")
