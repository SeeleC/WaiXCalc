# WaiXCalc

WaiXCalc实现了分数四则混合运算、算式分割、判断算式等功能。

如需包装好的程序，见[main](https://github.com/WaiZhong/WaiXCalc/)

此分支仅提供所需的函数。

## Install

    git clone git@github.com:WaiZhong/WaiXCalc.git

## Usage

### example

```python
import WaiXCalc
f = WaiXCalc.get_formula('1/2^3')
print(WaiXCalc.compute(f))
```
output:
```
1/8
```

## License

本仓库使用[MIT](LICENSE)协议。
