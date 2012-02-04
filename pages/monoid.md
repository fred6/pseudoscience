# monoid

A **monoid** is a semigroup $(S, \ast)$ which also contains an element $u$ of $S$, often called the **unit**, which has the following property:

$$ \forall a \in S \ a \ast u = u \ast a = a $$

We can prove that this element $u$ is unique: suppose $u'$ and $u$ are elements with the above property. Then $u = u \ast u'$ because $u'$ is a unit. But then $u \ast u' = u'$ because $u$ is a unit, so we've just proven $u = u'$, i.e. the unit is unique.

This allows us to redefine a monoid as a triple $(S, \ast, u)$ where $(S, \ast)$ is a semigroup and $u \in S$ such that for all $a \in S$, $a \ast u = u \ast a = a$. (One might even say that $u$ is a [nullary op][nullary_op] $u: \mathbf{1} \to S$ where $\mathbf{1}$ is a set with one element in it. A nullary operation is equivalent to picking an element out of the codomain).

[nullary_op]: http://en.wikipedia.org/wiki/Arity#Nullary
