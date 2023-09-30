# Boolean Reduction Notes

## Motivation

Using well known rules, a human can reduce a normal math expression even
if it has unknowns.

```python
# For example...

2(x + 5) - x - 10

= 2x + 10 - x - 10

= 2x - x + 10 - 10

= x
```

The same is the case for boolean expressions!

```python
(b and (not a)) or a

= (b or a) and ((not a) or a)

= (b or a) and True

= b or a
```

Is there a foolproof sequence of steps a computer could use 
to complete boolean reductions like the one above?

## AST Definition
```python
v(x)            # An identifier with name x.
imm(c)          # An immediate with value c in {0, 1}.

not(e)          # The logical negation of expression e.
or(e1, e2)      # The logical or of expressions e1 and e2.
and(e1, e2)     # The logical and of expressions e1 and e2.

if(e1, e2, e3)  # If e1 resolves to 1, then e2, otherwise e3. (Ternary)
                # NOTE e1 is known as the "condition", e2 as the "consequence",
                # and e3 as the "alternative".
```
__NOTE__ that all types above are themselves valid expressions.

#### Example

__ALSO NOTE__ that for the remainder of this document we will be transforming
the following expression as an example.

```python
or(
    and(
        v(b), 
        not(v(a))
    ), 
    v(a)
)
```
<p align="center">
    <img src="./pics/initial.svg">
</p>

## Algorithm

### `toIf` Definition

This function takes an expression and converts it into a equal if expression.

An __if expression__ is an expression which only contains variables, immediates, and
ternaries.


`toIf` depends on the following semantic equalities.

```python
not(e)      = if(e, imm(0), imm(1))
or(e1, e2)  = if(e1, imm(1), e2)
and(e1, e2) = if(e1, e2, imm(0))
```

`toIf` uses the above rules recursively...

```python
toIf(v(x))      = v(x)
toIf(imm(c))    = imm(c)

toIf(not(e)) = 
    if(toIf(e), 
        imm(0), imm(1))

toIf(or(e1, e2)) = 
    if(toIf(e1), 
        imm(1), toIf(e2))

toIf(and(e1, e2) = 
    if(toIf(e1), 
        toIf(e2), imm(0))

toIf(if(e1, e2, e3)) = 
    if(toIf(e1), 
        toIf(e2), toIf(e3))
```

#### Example
```python
# Initial 
or(
    and(
        v(b), 
        not(v(a))
    ), 
    v(a)
)
```
<p align="center">
    <img src="./pics/initial.svg">
</p>

```python
# toIf Part 1
or(
    and(
        v(b), 
        if(v(a), imm(0), imm(1))
    ), 
    v(a)
)
```

<p align="center">
    <img src="./pics/toIf1.svg">
</p>

```python
# toIf Part 2
or(
    if(
        v(b), 
        if(v(a), imm(0), imm(1)),
        imm(0)
    ), 
    v(a)
)
```

<p align="center">
    <img src="./pics/toIf2.svg">
</p>

```python
# toIf Part 3 
if(
    if(
        v(b), 
        if(v(a), imm(0), imm(1)),
        imm(0)
    ), 
    imm(1),
    v(a)
)
```

<p align="center">
    <img src="./pics/toIf3.svg">
</p>

### `norm` Definition

This function converts an if expression into a normal if expression. 

A __normal if expression__ is an if expression in which all condition expressions
are immediates or variables.

```python
# An example of a normal if expression.
if(imm(0), v(x), v(y))      # A normal if expression.

# An example of a non normal if expression.
# A ternary can never be itself a condition.
if(if(imm(0), v(x), v(y)), imm(1), imm(0))

# Note that standalone variables and immediates are also
# examples of normal if expressions
v(x)
imm(1)
```
The `norm` function abides by the following recursive definition.
```python
# First we define a helper funciton: join.
#
# This function takes an if expression whose 3 subexpressions 
# are normal and returns a semantically equal normal if 
# expression.

join(if(v(x), e2, e3))      = if(v(x), e2, e3)
join(if(imm(c), e2, e3))    = if(imm(c), e2, e3)

join(if(if(v(x), e2, e3), e4, e5)) =
    if(v(x), join(if(e2, e4, e5)), join(if(e3, e4, e5)))

join(if(if(imm(c), e2, e3), e4, e5)) =
    if(imm(c), join(if(e2, e4, e5)), join(if(e3, e4, e5)))

# Now for norm.

norm(v(x))   = v(x)
norm(imm(c)) = imm(c)

norm(if(e1, e2, e3)) = join(if(norm(e1), norm(e2), norm(e3)))
```

#### Example

```python
# Initial
if(
    if(
        v(b), 
        if(v(a), imm(0), imm(1)),
        imm(0)
    ), 
    imm(1),
    v(a)
)
```
<p align="center">
    <img src="./pics/norm0.svg">
</p>

```python
# Normed
if(
    v(b), 
    if(
        v(a), 
        if(imm(0), imm(1), v(a)), 
        if(imm(1), imm(1), v(a))
    ), 
    if(imm(0), imm(1), v(a))
)
```
<p align="center">
    <img src="./pics/norm.svg">
</p>

### `eval` Definition
This function converts a normal if expression into a equivalent, potentially reduced 
normal if expression.

```python
eval(v(x))    = v(x)
eval(imm(c))  = imm(c)

eval(if(imm(1), e2, e3)) = eval(e2)
eval(if(imm(0), e2, e3)) = eval(e3)

eval(if(v(x), e2, e3)) = 
    define
        r2 as eval(e2[v(x) <- imm(1)])
        r3 as eval(e3[v(x) <- imm(0)])
    in
        when r2 = r3 then r2
        when r2 = imm(1) and r3 = imm(0) then v(x)
        otherwise if(v(x), r2, r3)
```

#### Example

```python
# Initial
if(
    v(b), 
    if(
        v(a), 
        if(imm(0), imm(1), v(a)), 
        if(imm(1), imm(1), v(a))
    ), 
    if(imm(0), imm(1), v(a))
)
```
<p align="center">
    <img src="./pics/eval0.svg">
</p>

```python
# Eval Part 1
if(
    v(b), 
    if(
        v(a), 
        if(imm(0), imm(1), imm(1)), 
        if(imm(1), imm(1), v(a))
    ), 
    if(imm(0), imm(1), v(a))
)
```
<p align="center">
    <img src="./pics/eval1.svg">
</p>

```python
# Eval Part 2
if(
    v(b), 
    if(
        v(a), 
        imm(1),
        if(imm(1), imm(1), v(a))
    ), 
    if(imm(0), imm(1), v(a))
)
```
<p align="center">
    <img src="./pics/eval2.svg">
</p>

```python
# Eval Part 3
if(
    v(b), 
    if(
        v(a), 
        imm(1),
        if(imm(1), imm(1), v(0))
    ), 
    if(imm(0), imm(1), v(a))
)
```
<p align="center">
    <img src="./pics/eval3.svg">
</p>

```python
# Eval Part 4
if(
    v(b), 
    if(
        v(a), 
        imm(1),
        imm(1)
    ), 
    if(imm(0), imm(1), v(a))
)
```
<p align="center">
    <img src="./pics/eval4.svg">
</p>

```python
# Eval Part 5
if(
    v(b), 
    imm(1),
    if(imm(0), imm(1), v(a))
)
```
<p align="center">
    <img src="./pics/eval5.svg">
</p>

```python
# Eval Part 6
if(
    v(b), 
    imm(1),
    v(a)
)
```
<p align="center">
    <img src="./pics/eval6.svg">
</p>

### `reduce` Definition
This function converts an if expression back to a general boolean expression.

__NOTE__ `reduce` is the inverse of `toIf`.

```python
reduce(v(x))    = v(x)
reduce(imm(c))  = imm(c)

reduce(e1, imm(0), imm(1))  = not(reduce(e1))

reduce(e1, imm(1) e2)   = or(reduce(e1), reduce(e2))
reduce(e1, e2, imm(0))  = and(reduce(e1), reduce(e2))      
```

#### Example

```python
# Initial 
if(
    v(b), 
    imm(1),
    v(a)
)
```

<p align="center">
    <img src="./pics/reduce0.svg">
</p>

```python
# Reduced
or(v(b), v(a))
```

<p align="center">
    <img src="./pics/reduce.svg">
</p>

## Exponential Normal Forms

The largest pitfall of this algorithm is that some trees can grow exponentially 
when normalized. 

Note that I use the word *some*. If we structure our expressions correctly,
this problem can be avoided.

### Subtree Reuse

The above algorithm requires no mutation of trees. During each transformation,
if a tree needs to be *modified*, a new tree can instead be created and returned.

So, if we implement our transformations well, a single instance of a 
tree can appear as a subtree in multple trees.

As no tree can be modified, there is no threat of corrupting one tree
by using another.

Most notably, a single instance of a tree can appear as a subtree multple times
in the same parent tree.

<p align="center">
    <img src="./pics/unique_rep0.svg">
</p>

For example, imagine each node in the above tree resides in its own unique place
in memory. This approach would be wasteful as the same subtree (highlighted in red)
appears twice in the same tree.

Instead, it would be better to store the tree as follows.


<p align="center">
    <img src="./pics/unique_rep1.svg">
</p>

A strong implementation of the transformations above would ensure a new tree
is only constructed when needed. Thus, minimizing the true size of 
returned tree in memory.

### Ok, but what does this look like?

Here is a tree we are about to normalize. 
The outermost if expression isn't normal.
Addistionally, the consequce of the outermost isn't normal.

<p align="center">
    <img src="./pics/unique_norm_rep0.svg">
</p>

After we normalize, we may expect the resulting tree to 
look something like this.

<p align="center">
    <img src="./pics/unique_norm_rep1.svg">
</p>

However, by taking advantage of the power of immutability, a strong
implementation would instead produce the following tree.


<p align="center">
    <img src="./pics/unique_norm_rep2.svg">
</p>

### So, where's the problem?

Well, while our reduced graph above has many less nodes than its initial form,
it has the same number of paths from the root to the result nodes (g, h, and i).

If our reduced graph above were the final product, this wouldn't be a problem.

However, what if our reduced graph was actually in the condition position
Is there a way??? Is there a way to optimize this??




## Improvement Stragtegies 
