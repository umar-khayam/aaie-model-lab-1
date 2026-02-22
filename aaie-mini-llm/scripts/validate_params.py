from model.transformer import MiniGPT
from model.model_utils import count_parameters, format_params

def main():
    # Example config (Small)
    vocab_size = 50257
    max_seq_len = 256
    d_model = 768
    n_head = 12
    n_layer = 12
    d_ff = 3072
    dropout = 0.1
    tie_weights = True

    model = MiniGPT(
        vocab_size=vocab_size,
        max_seq_len=max_seq_len,
        d_model=d_model,
        n_head=n_head,
        n_layer=n_layer,
        d_ff=d_ff,
        dropout=dropout,
        tie_weights=tie_weights
    )

    total, trainable = count_parameters(model)
    print("Total params:", format_params(total))
    print("Trainable params:", format_params(trainable))

if __name__ == "__main__":
    main()
