"""
Short utility functions.
"""

import torch


def cumsum_shifted(xs):
    """
    Assumes `xs` is a 1-d array.
    The usual cumsum has elements [x[1], x[1] + x[2], ...]. This one has elements
    [0, x[1], x[1] + x[2], ...]. Useful for calculating sentence offsets.
    """
    cs = xs.cumsum(dim=0)
    shift = torch.zeros(1, dtype=torch.long, device=cs.device)  # Put on correct device.
    return torch.cat([shift, cs[:-1]], dim=0)


def batch_identity(batch_size, matrix_size, *args, **kwargs):
    """
    Tile the identity matrix along axis 0, `batch_size` times.
    """
    ident = torch.eye(matrix_size, *args, **kwargs).unsqueeze(0)
    res = ident.repeat(batch_size, 1, 1)
    return res


def fields_to_batches(dd, keys_to_ignore=[]):
    """
    The input is a dict whose items are batched tensors. The output is a list of dictionaries - one
    per entry in the batch - with the slices of the tensors for that entry. Here's an example.
    Input:
    d = {"a": [[1, 2], [3,4]], "b": [1, 2]}
    Output:
    res = [{"a": [1, 2], "b": 1}, {"a": [3, 4], "b": 2}].
    """
    # Make sure all input dicts have same length.
    # import pdb; pdb.set_trace()
    keys = [key for key in dd.keys() if key not in keys_to_ignore]
    lengths = [len(dd[k]) for k in keys]
    # 
    assert len(set(lengths)) == 1
    length = lengths[0]
    res = [{k: dd[k][i] for k in keys} for i in range(length)]
    return res


def batches_to_fields(batches):
    """
    The inverse of `fields_to_batches`.
    """
    # Make sure all the keys match.
    first_keys = batches[0].keys()
    for entry in batches[1:]:
        if set(entry.keys()) != set(first_keys):
            raise ValueError("Keys to not match on all entries.")

    res = {k: [] for k in first_keys}
    for batch in batches:
        for k, v in batch.items():
            res[k].append(v)

    return res
