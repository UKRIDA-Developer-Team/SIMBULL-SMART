| Method | Scope | Question it answers | In the app |
|---|---|---|---|
| **Exact Shapley values** (interventional SHAP) | local, RF stage | Which factors push this student's predicted anxiety up or down, and by how much? | Recommendation → Explainable AI → Anxiety prediction |
| **SMART contributions** (weight × utility) | local, SMART stage | Which criteria make the chosen alternative win? | Recommendation → From prediction to recommendation |
| **"What if" counterfactuals** | local, RF + SMART | What changes if one factor improves to a typical student's level? | Recommendation → What if? |
| **Permutation importance** | global, RF | How much does the error grow when one feature's information is removed? | this chapter |
| **PDP and ICE** | global, RF | How does the prediction move with one factor, on average and per student? | this chapter |
| **Gini importance** | global, RF | Which features do the trees use most to split the data? | Chapter 2 Model |

**Shapley values.** For a prediction *f(x)* and feature set *F* (11 features), the value of feature *i* is

$$
\phi_i = \sum_{S \subseteq F \setminus \{i\}} \frac{|S|!\,(|F|-|S|-1)!}{|F|!}\,\bigl[v(S \cup \{i\}) - v(S)\bigr],
$$

where *v(S)* = the mean prediction when the features in *S* take the student's values and the others take a reference student's values. There are only 2¹¹ = 2,048 coalitions, so all of them are computed (no sampling approximation). Properties checked by the automated tests: the φ add up to prediction − average (*efficiency*), a feature the model ignores gets 0 (*dummy*), and for a linear model φᵢ = βᵢ(xᵢ − x̄ᵢ).

**Limitations.** Interventional SHAP replaces feature values independently, so with correlated features (such as stress and burnout) it can create unusual combinations. Counterfactuals are model simulations, **not** proof of cause and effect. Every explanation describes the model's behaviour, not the student's clinical condition.
