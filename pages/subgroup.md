# subgroup

(First definition from Birkoff and Mac Lane):

Given groups $(S, \circ, v, \iota ')$ and $(G, \ast, u, \iota)$, where $S \cup G$, the group attached to $S$ is a **subgroup** of the group attached to $G$ iff the map $\phi S \to G$ defined by $\phi(x) = x$ for all $x \in S$ is a group morphism.

*[This definition is a bit cryptic, so I should show how this relates to S being closed under $\ast$ and $\circ$ being the restriction of $\ast$ to $S \times S \to S$]*

This proof is saved for later modification:

Let's prove this. Suppose first that $S$ is a group with group operation $\circ$ and $G$ is a group with group operation $\ast$, and that $\phi$ is a morphism. By the definition of a morphism, for all $a$ and $b \in S$:

$$ a \circ b = \phi(a \circ b) = \phi(a) \ast \phi(b) $$

But $\phi(a) = a$ and $\phi(b) = b$, so we now have $a \circ b = a \ast b$. So $\circ$ is actually the restriction of $G$'s group operation $\ast$ to $S$, proving it is a subgroup.

To prove the converse, notice that if $S$ is a subgroup of $G$, then when we define the function $\phi: S \to G$ by $\phi(x) = x$ for any $x \in S$, then, in particular, for $a$, $b \in S$, $\phi(a \ast b) = a \ast b$, which proves that $\phi$ is a morphism.

# stuff

I originally presented this definition of a subgroup:

Given some group $G$, a subset $S$ of $G$ is a **subgroup** of $G$ if:

1. $S$ is closed under $G$'s group operation, $\ast$
2. There is an element $e \in S$ such that for every $a \in S$, $a \ast e = e \ast a = a$.
3. for each $a \in S$ there's a $a' \in S$ such that $a \ast a' = a' \ast a = e$

But I'm ditching this approach because "S being closed under the same operation of G" is a sloppy way to word it. It's technically a different operation (uses different sets), but it takes the same values as G's group operation.

I'm also obscuring (or at least not making clear) the difference between some set being *closed* under an operation, and a binary operation on the set. A set is necessarily closed under a binary operation on that set, but the set might also be closed under operations of a superset, as is the case with subgroups.

Will clean this up.

Also, I need to stress, in defining a subgroup, that it's not enough for there to be some group whose set is a subset of another group. The set should also be closed *under the supergroup's group operation*, so that the restriction to the subset makes it a binary operation on the group. Although that makes me wonder if there are any examples of a group whose set is a subset of another group, but which *isn't* closed under the group operation of the supergroup.
