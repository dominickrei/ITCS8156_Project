from enum import Enum
import numpy as np
import os
import sys
import random
import torch

import torchvision
import torchvision.transforms as T
to_tensor = T.Compose([ T.ToTensor()])
normalize = T.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))

def seed_everything(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    

def normalize_vector(x):
    buffer = torch.pow(x, 2)
    normp = torch.sum(buffer, 1).add_(1e-10)
    normalization_constant = torch.sqrt(normp)
    output = torch.div(x, normalization_constant.view(-1, 1).expand_as(x))
    return output

def ensure_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
        
def save_model(model, save_dir, fname):
    ensure_folder(save_dir)
    torch.save(model.state_dict(), os.path.join(save_dir, fname))
    
def load_model(model, fn):
    model.load_state_dict(torch.load(fn))
    
def distance(x1, x2):
    # print_tensor_size(x1, x2)
    # print("in distance")
    diff = torch.abs(x1 - x2)
    return torch.pow(diff, 2).sum(dim=-1)

def cos_distance(x1, x2):
    cos = nn.CosineSimilarity(dim=1, eps=1e-6)
    return cos(x1, x2)
    
    
def align_videos(z1, z2):
    l, D = z1.size(0), z1.size(0)
    align = [-1] * l
    for i in range(l):
        x = z1[i:i+1]
        minidx = -1
        ds = distance(x.expand_as(z2).reshape(-1, D), z2.reshape(-1, D))
        minidx = torch.argmin(ds)
        align[i] = minidx
    # print (align)
    return align


def alignment_error(z1, z2):
    l, D = z1.size(0), z1.size(1)
    align = [-1] * l
    for i in range(l):
        x = z1[i:i+1]
        minidx = -1
        ds = distance(x.expand_as(z2).reshape(-1, D), z2.reshape(-1, D))
        minidx = torch.argmin(ds)
        align[i] = minidx
    # print (align)
    return np.mean([abs(i-align[i])/l for i in range(l)])

def cycle_error(z1, z2):
    l, D = z1.size(0), z1.size(1)
    align, align_rev = [-1]*l, [-1]*l
    for i in range(l):
        x = z1[i:i+1]
        ds = distance(x.expand_as(z2).reshape(-1, D), z2.reshape(-1, D))
        align[i] = torch.argmin(ds)
        y = z2[align[i]:align[i]+1]
        ds = distance(y.expand_as(z1).reshape(-1, D), z1.reshape(-1, D))
        align_rev[i] = torch.argmin(ds)
    return np.mean([abs(i-align_rev[i])/l for i in range(l)])


def kendalls_tau(z1, z2):
    l, D = z1.size(0), z1.size(1)
    align = [-1]*l
    for i in range(l):
        x = z1[i:i+1]
        ds = distance(x.expand_as(z2).reshape(-1, D), z2.reshape(-1, D))
        align[i] = torch.argmin(ds)
    concordant_pairs = 0
    for i in range(l):
        for j in range(i+1, l):
            if align[i] < align[j]:
                concordant_pairs += 1
    total = l*(l-1)/2
    return (concordant_pairs - (total - concordant_pairs)) / total
    
    
    
class Config(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    
class Summary(Enum):
    NONE = 0
    AVERAGE = 1
    SUM = 2
    COUNT = 3

class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self, name, fmt=':f', summary_type=Summary.AVERAGE):
        self.name = name
        self.fmt = fmt
        self.summary_type = summary_type
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count

    def __str__(self):
        fmtstr = '{name} {avg' + self.fmt + '}'
        return fmtstr.format(**self.__dict__)
    
    def summary(self):
        fmtstr = ''
        if self.summary_type is Summary.NONE:
            fmtstr = ''
        elif self.summary_type is Summary.AVERAGE:
            fmtstr = '{name} {avg:.3f}'
        elif self.summary_type is Summary.SUM:
            fmtstr = '{name} {sum:.3f}'
        elif self.summary_type is Summary.COUNT:
            fmtstr = '{name} {count:.3f}'
        else:
            raise ValueError('invalid summary type %r' % self.summary_type)
        
        return fmtstr.format(**self.__dict__)


class ProgressMeter(object):
    def __init__(self, num_batches, meters, prefix=""):
        self.batch_fmtstr = self._get_batch_fmtstr(num_batches)
        self.meters = meters
        self.prefix = prefix

    def display(self, batch):
        entries = [self.prefix + self.batch_fmtstr.format(batch)]
        entries += [str(meter) for meter in self.meters]
        print('\t'.join(entries))
        
    def display_summary(self):
        entries = [" *"]
        entries += [meter.summary() for meter in self.meters]
        print(' '.join(entries))

    def _get_batch_fmtstr(self, num_batches):
        num_digits = len(str(num_batches // 1))
        fmt = '{:' + str(num_digits) + 'd}'
        return '[' + fmt + '/' + fmt.format(num_batches) + ']'
    
    
def print_tensor_size(*tensors):
    print ([t.size() for t in tensors])