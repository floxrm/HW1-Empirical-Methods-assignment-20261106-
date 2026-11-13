# HW1 Group 15: meeting brief

2026-11-13

The four notebooks agree on almost every conclusion, but our own Question 2 (h) to (k) was wrong because of an integer overflow, which is now fixed, and we still need to settle a few conventions before we merge and submit on 16 November.

## Agenda (30 minutes)

| # | Topic | Min | Decision needed |
| --- | --- | --- | --- |
| 1 | Our Question 2 (h) to (k): bug now fixed | 5 | Confirm the corrected numbers and the rewritten answers |
| 2 | Assumptions we must state | 5 | Agree one wording for all answers |
| 3 | Method conventions in the code | 8 | Skewness and kurtosis estimator, robust standard errors, Sharpe ratio, Student-t overlay |
| 4 | Deviations in interpretation | 7 | Final wording for Question 2 (h), (i) and (k) |
| 5 | Merge and submit | 5 | Base notebook, header with names and IDs, who uploads |

## Decision 1: our age² was wrong and is now fixed

In the Stata file, age and fsize are stored as 8-bit integers, so squaring age silently wraps around (age 64 gives 0 instead of 4,096). Afonso, Hannah and Moritz convert the data to float64 first; our notebook did not until we fixed it. The corrected model reproduces the file's own agesq column, and all three teammates get identical numbers.

| Model (2), full sample | Ours before the fix | Correct |
| --- | --- | --- |
| Coefficient on age² | -0.0002 (p = 0.985) | 0.0264 (t = 4.67) |
| Coefficient on age | 1.021 | -1.258 |
| p-value of the income term | 0.031 | 0.084 |
| Coefficient on family size | -2.343 | -1.979 |
| R² | 0.1971 | 0.1989 |
| F-test in (i) | 136.1 | 147.3 |
| Age turning point | 3,242 years | 23.8 years |

What changed in our written answers (all four are already rewritten):

- (h): the age effect is not a constant 1,000 USD per year. It grows from about 60 USD per year at age 25 to about 1,900 USD at age 60, and it is positive for everyone older than 24, so for the whole sample.
- (i): both squared terms are significant (t = 16.3 for income² and 4.7 for age²), not only the income term.
- (j): same logic as before, with the corrected numbers (t of income = -1.73).
- (k): no coefficient changes its status at 5%. Income is insignificant before and after (t from -1.73 to -0.45), income² stays significant (t from 16.3 to 3.3).

Fix applied: the pension data is converted to float64 right after loading; (h) to (k) were re-run and now match Afonso, Hannah and Moritz.

## Assumptions we state in the answers

- **Returns:** all Question 1 statistics use monthly log returns, ln(1 + R), not annualised.
- **CAPM:** the risk-free rate is zero, as the task allows. Alpha is therefore not a true excess return: it equals the true alpha plus (1 - beta) times the risk-free rate, which overstates alpha for Coca-Cola and ExxonMobil. We say this once.
- **Decision rule:** 5% level; the 1% level only as a remark.
- **t-tests on means:** two-sided with 419 degrees of freedom. Returns are not Normal (Jarque-Bera rejects), but with 420 observations the sample mean is approximately Normal.
- **One-sided test in 2 (e):** valid only if the direction was fixed before looking at the data, so we report it together with the two-sided result.
- **Samples:** (c) to (g) and (l) use the 2,017 single-person households; (h) to (k) use all 9,275 households.
- **Units:** wealth and income are in thousands of USD, so one unit is 1,000 USD.
- **Rescaling in (j):** the square is rescaled consistently, (inc/100)²; keeping the old square gives the same t-values.

## Method conventions where the code differs

| Topic | Who does what | Proposal |
| --- | --- | --- |
| Skewness and kurtosis | Hannah, Moritz: pandas, bias-adjusted (EW excess kurtosis 2.83). Afonso, ours: scipy (2.78) | One estimator, named in the text; scipy matches Jarque-Bera |
| Robust standard errors | Afonso, Moritz: HC0. Hannah, ours: HC1 | HC1 (Stata's robust); no practical difference at n = 9,275 |
| Sharpe ratio in (f) | Afonso, Hannah, Moritz use mean divided by standard deviation. We dropped it because it needs a zero risk-free rate | Keep as a supporting line, labelled monthly with risk-free rate 0, as the CAPM part already assumes it |
| Student-t line in (h) | Afonso, Moritz fit it (4 to 5.5 degrees of freedom). Hannah, ours only name it | Add the fitted line: it answers "which distribution fits better" with evidence |
| Heteroskedasticity in (k) | Afonso, Moritz run Breusch-Pagan (p about 0). Hannah, ours argue in words | Add the one-line test |
| Extras and length | Moritz adds Newey-West, sub-periods, VaR, drawdowns, median regression, and is far longer than the others | Short core answer per part; extras labelled "additional" |
| Data paths | Teammates read the files from the notebook's folder; ours reads from a data folder | Files next to the notebook so the code runs for the grader |

## Deviations in interpretation

Question 1 and Question 2 (a) to (g) and (l) agree across all four notebooks: EW is the riskier index, no clear ranking of indices versus stocks for Normality, only Microsoft's alpha is significant, and the age test is rejected one-sided (p = 0.044) but not two-sided (p = 0.087). The differences are:

| Part | Difference | Proposal |
| --- | --- | --- |
| 2 (e) | Moritz also tests with robust standard errors: t = -1.32, p = 0.094, so no rejection | Add one sentence that the one-sided result is fragile |
| 2 (g) | Afonso and Hannah note that R² falls from 0.119 to 0.083 without age. We do not | Add the sentence |
| 2 (d) | Hannah: for a 25-year-old the model predicts negative wealth below an income of about 27,500 USD. Moritz: centred intercept equals mean wealth (13.6). We mention centring only | Keep centring, optionally add Hannah's example |
| 2 (h) | Ours was wrong, now fixed (see Decision 1). Others: age effect rises with age, family size costs about 1,980 USD | Done: ours now matches |
| 2 (i) | Ours said the rejection came from income only, now corrected. Others: both squares are significant, F = 147.3 | Done: ours now matches |
| 2 (k) | Ours said income loses significance, now corrected. Others: no change in significance at 5%, income² falls from t = 16.3 to 3.3 | Done: ours now matches |

## Merged solution and next steps

Proposal: use our notebook as the base, since it has one cell per sub-question with its answer directly below, with the overflow now fixed, and take over the additions above. Use Afonso's notebook as the numerical cross-check, because it is concise and correct. Moritz's notebook is the source for optional extras only.

- [ ] Done: pension data converted to float64, (h) to (k) re-run and the four answers rewritten in hw1_Flo.ipynb
- [ ] Add the Student-t line, the Breusch-Pagan line, the Sharpe line, the robust remark in (e) and the R² sentence in (g)
- [ ] Settle the conventions from agenda item 3 and use them in every part
- [ ] Header with group number 15 and names and IDs of all members; known so far: Afonso 43337, Moritz 43352; still missing: Hannah, Florian
- [ ] Run the notebook top to bottom on a clean kernel, with the data files next to it
- [ ] Export the PDF and name PDF and code file with the uploader's student ID; one member uploads by 2026-11-16
