LID Toolkit: Mathematical Walkthrough
Toy Example Setup
3 Languages: English (en), Spanish (es), Mandarin (zh)
2 Historical MKB Datasets: H1 = {en, es}, H2 = {en, zh}
1 Query Dataset: Q = {en, es, zh}
All stratum weights: $w_s = 1.0$ (equal weighting default)
Priority metric: f1_macro

10 Representative Features (stratum assignment follows first-match-wins priority in feature_stratifier.py:59-127):

| # | Feature Name | Stratum | Matching Pattern |
|---|---|---|---|
| f1 | "Plural word incidence" | S1_morphological | "plural word" |
| f2 | "Past tense incidence" | S1_morphological | "past tense" |
| f3 | "Type-token ratio" | S2_lexical_diversity | "type-token ratio" |
| f4 | "Hapax legomena ratio" | S2_lexical_diversity | "hapax legomena" |
| f5 | "Noun count incidence" | S3_structural | "" (catch-all) |
| f6 | "Mean sentence length (norm.)" | S3_structural | "" (catch-all) |
| f7 | "Word entropy" | S4_info_theoretic | "entropy" |
| f8 | "Zipf steepness" | S4_info_theoretic | "zipf steepness" |
| f9 | "Cosine distance sent-doc" | S5_cross_level | "cosine distance" |
| f10 | "Overlap count par-doc" | S5_cross_level | "overlap count" |
f7 is checked first against S4 patterns (line 61–65) before any S2 pattern, so "Word entropy" → S4, not S2.

Pooled Language Profiles (used for PCA fitting, after deduplication in MKBStore.finalise() at mkb_store.py:179-181):

$$
\mathbf{X}_{\text{pool}} = \begin{pmatrix}
 & \text{en} & \text{es} & \text{zh} \\
f_1 & 0.20 & 0.24 & 0.04 \\
f_2 & 0.30 & 0.40 & 0.10 \\
f_3 & 0.60 & 0.50 & 0.80 \\
f_4 & 0.40 & 0.30 & 0.60 \\
f_5 & 0.25 & 0.20 & 0.30 \\
f_6 & 0.67 & 0.80 & 0.40 \\
f_7 & 4.00 & 3.60 & 4.40 \\
f_8 & 1.20 & 1.00 & 1.60 \\
f_9 & 0.20 & 0.16 & 0.36 \\
f_{10} & 0.48 & 0.54 & 0.12
\end{pmatrix}
$$

Benchmark performances:

Dataset	Model A (fasttext_word) f1_macro	Model B (tfidf_lr) f1_macro
H1	0.82	0.79
H2	0.75	0.88
PHASE A — MKB Building
Step A.1 — Feature Stratification Assignment
Intuition: The 3,066 raw features encode wildly different linguistic phenomena. Grouping them before PCA preserves semantic coherence—morphological variance won't swamp structural variance in a joint decomposition. Code: feature_stratifier.py:132-139, _assign_stratum().

Formula:

$$
s(f) = \text{first stratum } s \in \mathcal{S} \text{ such that any pattern of } s \text{ is a substring of } \text{lower}(f)
$$

Substitution:

"Plural word incidence" → lower = "plural word incidence" → S4 check "entropy" ✗, S5 checks ✗, S1 check "plural word" ✓ → S1
"Word entropy" → lower = "word entropy" → S4 check "entropy" ✓ → S4 (checked before S2)
"Mean sentence length (norm.)" → S4 ✗, S5 ✗, S1 ✗, S2 ✗, S3 "" ✓ → S3
Result:

Stratum	Features
S1_morphological	f1, f2
S2_lexical_diversity	f3, f4
S3_structural	f5, f6
S4_info_theoretic	f7, f8
S5_cross_level	f9, f10
Step A.2 — Per-Stratum Standardisation
Intuition: Features within a stratum may have very different scales (e.g., f6 is a ratio 0–1 but f7 is entropy in bits 0–5). StandardScaler brings each column to zero mean and unit population-std, so PCA finds directions of relative variance rather than being dominated by the largest-scale feature. Code: feature_stratifier.py:222-225, FeatureStratifier.fit().

Formula:

$$
z_{ij} = \frac{x_{ij} - \mu_j}{\sigma_j}, \quad \mu_j = \frac{1}{n}\sum_i x_{ij}, \quad \sigma_j = \sqrt{\frac{1}{n}\sum_i(x_{ij}-\mu_j)^2}
$$

(sklearn StandardScaler uses population std, $\text{ddof}=0$)

Worked example — S1 sub-matrix (languages = rows, features = columns):

$$
\mathbf{X}_{S1} = \begin{pmatrix}
0.20 & 0.30 \\
0.24 & 0.40 \\
0.04 & 0.10
\end{pmatrix}
$$

Column means:
$$\mu_{f1} = \frac{0.20+0.24+0.04}{3} = 0.1600, \qquad \mu_{f2} = \frac{0.30+0.40+0.10}{3} = 0.2\overline{6}$$

Column standard deviations:
$$\sigma_{f1} = \sqrt{\frac{0.04^2+0.08^2+0.12^2}{3}} = \sqrt{\frac{0.0224}{3}} = 0.08641$$

$$\sigma_{f2} = \sqrt{\frac{0.0\overline{3}^2+0.1\overline{3}^2+0.1\overline{6}^2}{3}} = \sqrt{\frac{0.04\overline{6}}{3}} = 0.12472$$

Result — Standardised S1 matrix:

$$
\mathbf{Z}_{S1} = \begin{pmatrix}
+0.4629 & +0.2673 \\
+0.9258 & +1.0690 \\
-1.3887 & -1.3363
\end{pmatrix}
\quad \text{(rows: en, es, zh)}
$$

Verification: each column sums to $\approx 0$. ✓

The same procedure is applied independently to S2, S3, S4, S5 (scalers saved inside StratumFit.scaler).

Step A.3 — PCA per Stratum
Intuition: Within S1, "plural words" and "past tense" are both expressions of morphological richness. PCA finds the single axis that best separates morphologically-rich languages (en, es) from isolating ones (zh), discarding nearly-zero orthogonal variance. The retained PCs are the linguistically-meaningful "features" used downstream. Code: feature_stratifier.py:228-246.

Formula (covariance matrix and eigendecomposition):

$$
\mathbf{C} = \frac{1}{n-1}\mathbf{Z}^{\top}\mathbf{Z}, \qquad \mathbf{C}\mathbf{v}_k = \lambda_k \mathbf{v}_k
$$

Number of components retained:

$$
K = \min\left\{k \,:\, \sum_{i=1}^{k}\frac{\lambda_i}{\sum_j \lambda_j} \geq 0.95\right\}
$$

Substitution — S1:

$$
\mathbf{C}_{S1} = \frac{\mathbf{Z}_{S1}^{\top}\mathbf{Z}_{S1}}{2}
$$

$$
C_{00} = \frac{0.4629^2 + 0.9258^2 + 1.3887^2}{2} = \frac{3.0000}{2} = 1.5000
$$

$$
C_{11} = \frac{0.2673^2 + 1.0690^2 + 1.3363^2}{2} = \frac{3.0000}{2} = 1.5000
$$

$$
C_{01} = \frac{(0.4629)(0.2673) + (0.9258)(1.0690) + (-1.3887)(-1.3363)}{2} = \frac{2.9690}{2} = 1.4845
$$

$$
\mathbf{C}_{S1} = \begin{pmatrix}
1.5000 & 1.4845 \\
1.4845 & 1.5000
\end{pmatrix}
$$

For any symmetric $\begin{pmatrix}a & b \\ b & a\end{pmatrix}$, eigenvalues are $\lambda = a \pm b$:

$$
\lambda_1 = 1.5000 + 1.4845 = 2.9845, \qquad \lambda_2 = 1.5000 - 1.4845 = 0.0155
$$

Explained variance ratio:

$$
r_1 = \frac{2.9845}{2.9845 + 0.0155} = \frac{2.9845}{3.0000} = 99.5\% \geq 95\%
$$

Result: Keep $K_{S1} = 1$ PC. Eigenvector:

$$
\mathbf{v}_1^{(S1)} = \begin{pmatrix} 1/\sqrt{2} \\ 1/\sqrt{2} \end{pmatrix} = \begin{pmatrix} 0.7071 \\ 0.7071 \end{pmatrix}
$$

PC1 projection scores $p_i = \mathbf{Z}_{S1}[i,:] \cdot \mathbf{v}_1$:

$$
p_{\text{en}}^{S1} = 0.7071(0.4629 + 0.2673) = 0.7071 \times 0.7302 = \mathbf{0.5163}
$$
$$
p_{\text{es}}^{S1} = 0.7071(0.9258 + 1.0690) = 0.7071 \times 1.9948 = \mathbf{1.4105}
$$
$$
p_{\text{zh}}^{S1} = 0.7071(-1.3887 - 1.3363) = 0.7071 \times (-2.7250) = \mathbf{-1.9262}
$$

Check: $0.5163 + 1.4105 - 1.9262 = +0.0006 \approx 0$ ✓

Linguistic interpretation: PC1 is a "morphological richness" axis. Spanish (highest inflection) → +1.41; English (moderate) → +0.52; Mandarin (isolating, no inflectional morphology) → −1.93.

The same procedure applied to all 5 strata. Condensed results (full arithmetic available on request for each):

Stratum	PC1 direction	$\lambda_1/\sum\lambda$	en PC1	es PC1	zh PC1
S1	$[+0.707, +0.707]$	99.5%	+0.5163	+1.4105	−1.9262
S2	$[+0.707, +0.707]$	100%	−0.3780	−1.5121	+1.8900
S3	$[+0.707, -0.707]$	98.98%	−0.1982	−1.6162	+1.8142
S4	$[+0.707, +0.707]$	99.1%	−0.1890	−1.6221	+1.8112
S5	$[+0.707, -0.707]$	99.9%	−0.7085	−1.2645	+1.9731
S2 key numbers: $\mu_{f3}=0.6333$, $\sigma_{f3}=0.12472$; $\mu_{f4}=0.4333$, $\sigma_{f4}=0.12472$. After standardisation the two columns are identical ($r=1.0$), so PC1 explains 100% and $\mathbf{v}_1 = [0.707, 0.707]$.

S3 key numbers: f5 and f6 move in opposite directions across languages (zh has more nouns but shorter sentences). Cov matrix $\mathbf{C}_{S3} = \begin{pmatrix}1.5 & -1.4695 \\ -1.4695 & 1.5\end{pmatrix}$. Larger eigenvalue $\lambda_1 = 1.5 + 1.4695 = 2.9695$ → $\mathbf{v}_1 = [+0.707, -0.707]$. PC1 = (noun density) − (sentence length). zh scores highest: short sentences packed with content words.

Step A.4 — Dataset Fingerprint: Continuous Block
Intuition: A single dataset contains multiple languages. We need one fixed-length vector to represent the distribution of linguistic properties across those languages. For each PC within each stratum, we record five aggregate statistics: the mean, spread (std), extremes (min, max), and heterogeneity (Bessel-corrected std). Code: fingerprint_builder.py:92-113, FingerprintBuilder.build().

Formula:

$$
\text{FP}[s, k, \cdot] = \Big(\,\underbrace{\bar{p}}_{\text{mean}},\; \underbrace{\sigma_0}_{\text{std, ddof=0}},\; \underbrace{\min p}_{\text{min}},\; \underbrace{\max p}_{\text{max}},\; \underbrace{\sigma_1}_{\text{het, ddof=1}}\,\Big)
$$

where $p = \{p_l^{(s,k)} : l \in \text{languages of dataset}\}$.

For $n=2$ languages with scores $a, b$: $\bar{p}=\tfrac{a+b}{2}$, $\sigma_0 = \tfrac{|a-b|}{2}$, $\sigma_1 = \tfrac{|a-b|}{\sqrt{2}}$.

Substitution — H1 (languages: en, es), Stratum S1:

$$a = p_{\text{en}}^{S1} = 0.5163, \qquad b = p_{\text{es}}^{S1} = 1.4105$$

H1 Fingerprint — Continuous Block (languages: en, es)
S1 — Substitution:

$$a = p_{\text{en}}^{S1} = +0.5163, \qquad b = p_{\text{es}}^{S1} = +1.4105$$

$$\bar{p} = \frac{0.5163 + 1.4105}{2} = \frac{1.9268}{2} = +0.9634$$

$$\sigma_0 = \frac{|0.5163 - 1.4105|}{2} = \frac{0.8942}{2} = +0.4471$$

$$\sigma_1 = \frac{0.8942}{\sqrt{2}} = \frac{0.8942}{1.4142} = +0.6323$$

$$\text{H1}_{S1} = \{\text{mean}=+0.9634,\; \text{std}=+0.4471,\; \text{min}=+0.5163,\; \text{max}=+1.4105,\; \text{het}=+0.6323\}$$

S2 — Substitution:

$$a = -0.3780, \qquad b = -1.5121$$

$$\bar{p} = \frac{-0.3780 + (-1.5121)}{2} = -0.9451, \qquad \sigma_0 = \frac{1.1341}{2} = +0.5671, \qquad \sigma_1 = \frac{1.1341}{1.4142} = +0.8021$$

$$\text{H1}_{S2} = \{-0.9451,\; +0.5671,\; -1.5121,\; -0.3780,\; +0.8021\}$$

S3 — Substitution:

$$a = -0.1982, \qquad b = -1.6162$$

$$\bar{p} = -0.9072, \qquad \sigma_0 = \frac{1.4180}{2} = +0.7090, \qquad \sigma_1 = \frac{1.4180}{1.4142} = +1.0027$$

$$\text{H1}_{S3} = \{-0.9072,\; +0.7090,\; -1.6162,\; -0.1982,\; +1.0027\}$$

S4 — Substitution:

$$a = -0.1890, \qquad b = -1.6221$$

$$\bar{p} = -0.9056, \qquad \sigma_0 = \frac{1.4331}{2} = +0.7166, \qquad \sigma_1 = \frac{1.4331}{1.4142} = +1.0134$$

$$\text{H1}_{S4} = \{-0.9056,\; +0.7166,\; -1.6221,\; -0.1890,\; +1.0134\}$$

S5 — Substitution:

$$a = -0.7085, \qquad b = -1.2645$$

$$\bar{p} = -0.9865, \qquad \sigma_0 = \frac{0.5560}{2} = +0.2780, \qquad \sigma_1 = \frac{0.5560}{1.4142} = +0.3932$$

$$\text{H1}_{S5} = \{-0.9865,\; +0.2780,\; -1.2645,\; -0.7085,\; +0.3932\}$$

Result — H1 continuous block: $5 \text{ strata} \times 1 \text{ PC} \times 5 \text{ stats} = \mathbf{25}$ dimensions.

H2 Fingerprint — Continuous Block (languages: en, zh)
S1 — Substitution:

$$a = p_{\text{en}}^{S1} = +0.5163, \qquad b = p_{\text{zh}}^{S1} = -1.9262$$

$$\bar{p} = \frac{0.5163 - 1.9262}{2} = -0.7050, \qquad \sigma_0 = \frac{2.4425}{2} = +1.2213, \qquad \sigma_1 = \frac{2.4425}{1.4142} = +1.7267$$

$$\text{H2}_{S1} = \{-0.7050,\; +1.2213,\; -1.9262,\; +0.5163,\; +1.7267\}$$

S2 — Substitution:

$$a = -0.3780, \qquad b = +1.8900$$

$$\bar{p} = +0.7560, \qquad \sigma_0 = \frac{2.2680}{2} = +1.1340, \qquad \sigma_1 = \frac{2.2680}{1.4142} = +1.6039$$

$$\text{H2}_{S2} = \{+0.7560,\; +1.1340,\; -0.3780,\; +1.8900,\; +1.6039\}$$

S3 — Substitution:

$$a = -0.1982, \qquad b = +1.8142$$

$$\bar{p} = +0.8080, \qquad \sigma_0 = \frac{2.0124}{2} = +1.0062, \qquad \sigma_1 = \frac{2.0124}{1.4142} = +1.4232$$

$$\text{H2}_{S3} = \{+0.8080,\; +1.0062,\; -0.1982,\; +1.8142,\; +1.4232\}$$

S4 — Substitution:

$$a = -0.1890, \qquad b = +1.8112$$

$$\bar{p} = +0.8111, \qquad \sigma_0 = \frac{2.0002}{2} = +1.0001, \qquad \sigma_1 = \frac{2.0002}{1.4142} = +1.4144$$

$$\text{H2}_{S4} = \{+0.8111,\; +1.0001,\; -0.1890,\; +1.8112,\; +1.4144\}$$

S5 — Substitution:

$$a = -0.7085, \qquad b = +1.9731$$

$$\bar{p} = +0.6323, \qquad \sigma_0 = \frac{2.6816}{2} = +1.3408, \qquad \sigma_1 = \frac{2.6816}{1.4142} = +1.8965$$

$$\text{H2}_{S5} = \{+0.6323,\; +1.3408,\; -0.7085,\; +1.9731,\; +1.8965\}$$

Step A.5 — Dataset Fingerprint: Categorical S6 Block (Typology Flags)
Intuition: PCA is meaningless for nominal properties like script type or language family — you cannot interpolate between "Latin script" and "CJK script" on a continuous axis. These flags capture hard linguistic constraints that are strongly predictive of which LID models can handle the data at all. They are never PCA-compressed. Code: fingerprint_builder.py:114-117 → typology_lookup.py:141-174, dataset_typology_flags().

Formula:

$$
\text{FP}[\text{cat}] = \text{dataset\_typology\_flags}(\text{iso\_codes})
$$

Returns 17 aggregate scalars over all languages in the dataset (counts, fractions, binary flags).

Substitution — H1 (iso_codes = ['en', 'es']):

From typology_lookup.py:44-80:

en: tonal=F, scripts={latin}, morph=fusional, family=germanic, agglutinative=F, polysyllabic=T
es: tonal=F, scripts={latin}, morph=fusional, family=romance, agglutinative=F, polysyllabic=T
$$
\begin{array}{lll}
\texttt{cat\_\_n\_languages} = 2 & \texttt{cat\_\_n\_tonal} = 0 & \texttt{cat\_\_has\_tonal} = 0 \\
\texttt{cat\_\_n\_script\_types} = 1 & \texttt{cat\_\_has\_cjk} = 0 & \texttt{cat\_\_has\_latin} = 1 \\
\texttt{cat\_\_n\_agglutinative} = 0 & \texttt{cat\_\_frac\_agglutinative} = 0.0 & \texttt{cat\_\_n\_isolating} = 0 \\
\texttt{cat\_\_n\_polysyllabic} = 2 & \texttt{cat\_\_n\_language\_families} = 2 & \texttt{cat\_\_frac\_germanic} = 0.5 \\
\texttt{cat\_\_frac\_romance} = 0.5 & \texttt{cat\_\_frac\_slavic} = 0.0 & \texttt{cat\_\_has\_cyrillic} = 0 \\
\texttt{cat\_\_has\_greek} = 0 & \texttt{cat\_\_has\_hangul} = 0 &
\end{array}
$$

Substitution — H2 (iso_codes = ['en', 'zh']):

From typology_lookup.py:112-115:

zh: tonal=T, scripts={cjk}, morph=isolating, family=sino-tibetan, agglutinative=F, polysyllabic=F
$$
\begin{array}{lll}
\texttt{cat\_\_n\_languages} = 2 & \texttt{cat\_\_n\_tonal} = \mathbf{1} & \texttt{cat\_\_has\_tonal} = \mathbf{1} \\
\texttt{cat\_\_n\_script\_types} = \mathbf{2} & \texttt{cat\_\_has\_cjk} = \mathbf{1} & \texttt{cat\_\_has\_latin} = 1 \\
\texttt{cat\_\_n\_agglutinative} = 0 & \texttt{cat\_\_frac\_agglutinative} = 0.0 & \texttt{cat\_\_n\_isolating} = \mathbf{1} \\
\texttt{cat\_\_n\_polysyllabic} = \mathbf{1} & \texttt{cat\_\_n\_language\_families} = 2 & \texttt{cat\_\_frac\_germanic} = 0.5 \\
\texttt{cat\_\_frac\_romance} = 0.0 & \texttt{cat\_\_frac\_slavic} = 0.0 & \texttt{cat\_\_has\_cyrillic} = 0 \\
\texttt{cat\_\_has\_greek} = 0 & \texttt{cat\_\_has\_hangul} = 0 &
\end{array}
$$

Result: H1 and H2 each have $25 + 17 = \mathbf{42}$-dimensional fingerprints. The MKB store is now finalised.

PHASE B — Inference (Query Dataset Q)
Step B.1 — Query Fingerprint: Projecting Q through the Fitted Stratifier
Intuition: The query dataset Q = {en, es, zh} must be compressed using the same scaler parameters and PCA eigenvectors fitted in Phase A — not re-fitted. This ensures the query lives in the same latent space as the historical fingerprints, making distance comparisons meaningful. Code: feature_stratifier.py:261-294, FeatureStratifier.transform().

Formula:

$$
\mathbf{z}_l^{(s)} = \text{scaler}_s^{-1}(\mathbf{x}_l^{(s)}), \qquad p_l^{(s)} = \mathbf{v}_1^{(s)} \cdot \mathbf{z}_l^{(s)}
$$

Raw features for Q:

$$
\mathbf{X}_Q = \begin{pmatrix}
 & \text{en} & \text{es} & \text{zh} \\
f_1 & 0.21 & 0.23 & 0.05 \\
f_2 & 0.31 & 0.38 & 0.11 \\
f_3 & 0.58 & 0.52 & 0.78 \\
f_4 & 0.38 & 0.32 & 0.58 \\
f_5 & 0.26 & 0.21 & 0.31 \\
f_6 & 0.68 & 0.82 & 0.41 \\
f_7 & 4.10 & 3.50 & 4.30 \\
f_8 & 1.15 & 1.05 & 1.55 \\
f_9 & 0.22 & 0.18 & 0.34 \\
f_{10} & 0.50 & 0.52 & 0.14
\end{pmatrix}
$$

S1 — en: $\mu=[0.1600,\,0.2\overline{6}]$, $\sigma=[0.08641,\,0.12472]$, $\mathbf{v}_1=[0.7071,\,0.7071]$

$$
z_{f1} = \frac{0.21-0.16}{0.08641} = \frac{0.05}{0.08641} = +0.5786, \qquad z_{f2} = \frac{0.31-0.2\overline{6}}{0.12472} = \frac{0.04\overline{3}}{0.12472} = +0.3474
$$

$$
p_{\text{en,Q}}^{S1} = 0.7071 \times (0.5786 + 0.3474) = 0.7071 \times 0.9260 = +0.6548
$$

S1 — es:

$$
z_{f1} = \frac{0.23-0.16}{0.08641} = +0.8100, \qquad z_{f2} = \frac{0.38-0.2\overline{6}}{0.12472} = +0.9086
$$

$$
p_{\text{es,Q}}^{S1} = 0.7071 \times (0.8100 + 0.9086) = 0.7071 \times 1.7186 = +1.2152
$$

S1 — zh:

$$
z_{f1} = \frac{0.05-0.16}{0.08641} = -1.2730, \qquad z_{f2} = \frac{0.11-0.2\overline{6}}{0.12472} = -1.3361
$$

$$
p_{\text{zh,Q}}^{S1} = 0.7071 \times (-1.2730 - 1.3361) = 0.7071 \times (-2.6091) = -1.8450
$$

Check: $0.6548 + 1.2152 - 1.8450 = +0.025$ — small non-zero because Q's features differ slightly from the training pool. ✓ (expected)

Aggregate Q S1 block ($n=3$ languages):

$$\bar{p} = \frac{0.6548+1.2152-1.8450}{3} = \frac{0.0250}{3} = +0.0083$$

Deviations: $[+0.6465,\;+1.2069,\;-1.8533]$

$$\text{SS} = 0.6465^2 + 1.2069^2 + 1.8533^2 = 0.4180 + 1.4566 + 3.4347 = 5.3093$$

$$\sigma_0 = \sqrt{\frac{5.3093}{3}} = \sqrt{1.7698} = 1.3303, \qquad \sigma_1 = \sqrt{\frac{5.3093}{2}} = \sqrt{2.6547} = 1.6294$$

$$\boxed{\text{Q}_{S1} = \{+0.0083,\;+1.3303,\;-1.8450,\;+1.2152,\;+1.6294\}}$$

S2 projection (scaler: $\mu_{f3}=0.6333$, $\sigma_{f3}=0.12472$; $\mu_{f4}=0.4333$, $\sigma_{f4}=0.12472$; $\mathbf{v}_1^{S2}=[0.7071,0.7071]$):

$$
p_{\text{en,Q}}^{S2} = 0.7071\!\left(\frac{0.58-0.6333}{0.12472}+\frac{0.38-0.4333}{0.12472}\right) = 0.7071\!\left(-0.4274-0.4274\right) = 0.7071\times(-0.8548) = -0.6044
$$

$$
p_{\text{es,Q}}^{S2} = 0.7071\!\left(\frac{0.52-0.6333}{0.12472}+\frac{0.32-0.4333}{0.12472}\right) = 0.7071\times(-0.9086-0.9086) = 0.7071\times(-1.8172) = -1.2848
$$

$$
p_{\text{zh,Q}}^{S2} = 0.7071\!\left(\frac{0.78-0.6333}{0.12472}+\frac{0.58-0.4333}{0.12472}\right) = 0.7071\times(1.1762+1.1762) = 0.7071\times 2.3524 = +1.6638
$$

Aggregate: $\bar{p}=\tfrac{-0.6044-1.2848+1.6638}{3}=-0.0751$, SS=$0.5293^2+1.2097^2+1.7389^2=0.2802+1.4634+3.0238=4.7674$

$$\boxed{\text{Q}_{S2} = \{-0.0751,\;+1.2606,\;-1.2848,\;+1.6638,\;+1.5440\}}$$

S3 projection (scaler: $\mu_{f5}=0.25$, $\sigma_{f5}=0.04082$; $\mu_{f6}=0.6233$, $\sigma_{f6}=0.16660$; $\mathbf{v}_1^{S3}=[+0.7071,-0.7071]$):

$$
p_{\text{en,Q}}^{S3} = 0.7071\!\left(\frac{0.26-0.25}{0.04082}-\frac{0.68-0.6233}{0.16660}\right) = 0.7071\times(+0.2449-0.3402) = 0.7071\times(-0.0953) = -0.0674
$$

$$
p_{\text{es,Q}}^{S3} = 0.7071\!\left(\frac{0.21-0.25}{0.04082}-\frac{0.82-0.6233}{0.16660}\right) = 0.7071\times(-0.9798-1.1806) = 0.7071\times(-2.1604) = -1.5277
$$

$$
p_{\text{zh,Q}}^{S3} = 0.7071\!\left(\frac{0.31-0.25}{0.04082}-\frac{0.41-0.6233}{0.16660}\right) = 0.7071\times(+1.4697+1.2803) = 0.7071\times 2.7500 = +1.9445
$$

Aggregate: $\bar{p}=\tfrac{-0.0674-1.5277+1.9445}{3}=+0.1165$, SS=$0.1839^2+1.6442^2+1.8280^2=0.0338+2.7034+3.3416=6.0788$

$$\boxed{\text{Q}_{S3} = \{+0.1165,\;+1.4235,\;-1.5277,\;+1.9445,\;+1.7435\}}$$

S4 projection (scaler: $\mu_{f7}=4.00$, $\sigma_{f7}=0.32660$; $\mu_{f8}=1.2\overline{6}$, $\sigma_{f8}=0.24944$; $\mathbf{v}_1^{S4}=[+0.7071,+0.7071]$):

$$
p_{\text{en,Q}}^{S4} = 0.7071\!\left(\frac{4.10-4.00}{0.32660}+\frac{1.15-1.2\overline{6}}{0.24944}\right) = 0.7071\times(+0.3062-0.4679) = 0.7071\times(-0.1617) = -0.1143
$$

$$
p_{\text{es,Q}}^{S4} = 0.7071\!\left(\frac{3.50-4.00}{0.32660}+\frac{1.05-1.2\overline{6}}{0.24944}\right) = 0.7071\times(-1.5309-0.8689) = 0.7071\times(-2.3998) = -1.6974
$$

$$
p_{\text{zh,Q}}^{S4} = 0.7071\!\left(\frac{4.30-4.00}{0.32660}+\frac{1.55-1.2\overline{6}}{0.24944}\right) = 0.7071\times(+0.9187+1.1358) = 0.7071\times 2.0545 = +1.4527
$$

Aggregate: $\bar{p}=\tfrac{-0.1143-1.6974+1.4527}{3}=-0.1197$, SS=$0.0054^2+1.5777^2+1.5724^2\approx 0+2.4891+2.4724=4.9615$

$$\boxed{\text{Q}_{S4} = \{-0.1197,\;+1.2860,\;-1.6974,\;+1.4527,\;+1.5751\}}$$

S5 projection (scaler: $\mu_{f9}=0.24$, $\sigma_{f9}=0.08641$; $\mu_{f10}=0.38$, $\sigma_{f10}=0.18547$; $\mathbf{v}_1^{S5}=[+0.7071,-0.7071]$):

$$
p_{\text{en,Q}}^{S5} = 0.7071\!\left(\frac{0.22-0.24}{0.08641}-\frac{0.50-0.38}{0.18547}\right) = 0.7071\times(-0.2315-0.6471) = 0.7071\times(-0.8786) = -0.6213
$$

$$
p_{\text{es,Q}}^{S5} = 0.7071\!\left(\frac{0.18-0.24}{0.08641}-\frac{0.52-0.38}{0.18547}\right) = 0.7071\times(-0.6944-0.7549) = 0.7071\times(-1.4493) = -1.0248
$$

$$
p_{\text{zh,Q}}^{S5} = 0.7071\!\left(\frac{0.34-0.24}{0.08641}-\frac{0.14-0.38}{0.18547}\right) = 0.7071\times(+1.1573+1.2940) = 0.7071\times 2.4513 = +1.7338
$$

Aggregate: $\bar{p}=\tfrac{-0.6213-1.0248+1.7338}{3}=+0.0292$, SS=$0.6505^2+1.0540^2+1.7046^2=0.4232+1.1109+2.9057=4.4398$

$$\boxed{\text{Q}_{S5} = \{+0.0292,\;+1.2166,\;-1.0248,\;+1.7338,\;+1.4899\}}$$

Step B.2 — Query Fingerprint: Categorical S6 Block
Intuition: The same typology aggregation is run on Q's language set. Code: fingerprint_builder.py:114-117, typology_lookup.py:141.

Substitution — Q iso_codes = ['en', 'es', 'zh']. zh contributes: tonal=T, scripts={cjk}, morph=isolating, polysyllabic=F.

$$
\begin{array}{lll}
\texttt{cat\_\_n\_languages} = 3 & \texttt{cat\_\_n\_tonal} = 1 & \texttt{cat\_\_has\_tonal} = 1 \\
\texttt{cat\_\_n\_script\_types} = 2 & \texttt{cat\_\_has\_cjk} = 1 & \texttt{cat\_\_has\_latin} = 1 \\
\texttt{cat\_\_n\_agglutinative} = 0 & \texttt{cat\_\_frac\_agglutinative} = 0.0 & \texttt{cat\_\_n\_isolating} = 1 \\
\texttt{cat\_\_n\_polysyllabic} = 2 & \texttt{cat\_\_n\_language\_families} = 3 & \texttt{cat\_\_frac\_germanic} = 0.\overline{3} \\
\texttt{cat\_\_frac\_romance} = 0.\overline{3} & \texttt{cat\_\_frac\_slavic} = 0.0 &
\end{array}
$$

Step B.3 — Per-Stratum Euclidean Distance (S1–S5)
Intuition: In PCA space, Euclidean distance is the right metric — axes are orthogonal and variance-normalised. We compare Q's 5-element stratum slice (mean, std, min, max, het) against each historical dataset's corresponding slice. Large distance on S1 means the morphological diversity profile of the new dataset is unlike the historical one. Code: mkb_similarity.py:359-395, SimilarityEngine._stratum_distances().

Formula:

$$
d_s(Q, H) = \left\|\mathbf{v}_Q^{(s)} - \mathbf{v}_H^{(s)}\right\|_2 = \sqrt{\sum_{j=1}^{5} \left(v_{Q,j}^{(s)} - v_{H,j}^{(s)}\right)^2}
$$

d_S1(Q, H1)
$$
\mathbf{v}_Q^{S1} = [+0.0083,\;+1.3303,\;-1.8450,\;+1.2152,\;+1.6294]
$$
$$
\mathbf{v}_{H1}^{S1} = [+0.9634,\;+0.4471,\;+0.5163,\;+1.4105,\;+0.6323]
$$

$$
\Delta = [-0.9551,\;+0.8832,\;-2.3613,\;-0.1953,\;+0.9971]
$$

$$
d_{S1}(Q,H1) = \sqrt{0.9551^2 + 0.8832^2 + 2.3613^2 + 0.1953^2 + 0.9971^2}
= \sqrt{0.9122 + 0.7800 + 5.5757 + 0.0381 + 0.9942} = \sqrt{8.3002} = \mathbf{2.8810}
$$

d_S1(Q, H2)
$$
\mathbf{v}_{H2}^{S1} = [-0.7050,\;+1.2213,\;-1.9262,\;+0.5163,\;+1.7267]
$$

$$
\Delta = [+0.7133,\;+0.1090,\;+0.0812,\;+0.6989,\;-0.0973]
$$

$$
d_{S1}(Q,H2) = \sqrt{0.7133^2 + 0.1090^2 + 0.0812^2 + 0.6989^2 + 0.0973^2}
= \sqrt{0.5088+0.0119+0.0066+0.4885+0.0095} = \sqrt{1.0253} = \mathbf{1.0126}
$$

d_S2(Q, H1)
$$
\mathbf{v}_Q^{S2} = [-0.0751,\;+1.2606,\;-1.2848,\;+1.6638,\;+1.5440]
$$
$$
\mathbf{v}_{H1}^{S2} = [-0.9451,\;+0.5671,\;-1.5121,\;-0.3780,\;+0.8021]
$$

$$
\Delta = [+0.8700,\;+0.6935,\;+0.2273,\;+2.0418,\;+0.7419]
$$

$$
d_{S2}(Q,H1) = \sqrt{0.8700^2+0.6935^2+0.2273^2+2.0418^2+0.7419^2}
= \sqrt{0.7569+0.4809+0.0517+4.1689+0.5504} = \sqrt{6.0088} = \mathbf{2.4514}
$$

d_S2(Q, H2)
$$
\mathbf{v}_{H2}^{S2} = [+0.7560,\;+1.1340,\;-0.3780,\;+1.8900,\;+1.6039]
$$

$$
\Delta = [-0.8311,\;+0.1266,\;-0.9068,\;-0.2262,\;-0.0599]
$$

$$
d_{S2}(Q,H2) = \sqrt{0.6907+0.0160+0.8223+0.0512+0.0036} = \sqrt{1.5838} = \mathbf{1.2585}
$$

d_S3(Q, H1)
$$\Delta = [+0.1165-(-0.9072),\;+1.4235-0.7090,\;-1.5277-(-1.6162),\;+1.9445-(-0.1982),\;+1.7435-1.0027]$$
$$= [+1.0237,\;+0.7145,\;+0.0885,\;+2.1427,\;+0.7408]$$

$$
d_{S3}(Q,H1) = \sqrt{1.0480+0.5105+0.0078+4.5912+0.5488} = \sqrt{6.7063} = \mathbf{2.5897}
$$

d_S3(Q, H2)
$$\Delta = [+0.1165-0.8080,\;+1.4235-1.0062,\;-1.5277-(-0.1982),\;+1.9445-1.8142,\;+1.7435-1.4232]$$
$$= [-0.6915,\;+0.4173,\;-1.3295,\;+0.1303,\;+0.3203]$$

$$
d_{S3}(Q,H2) = \sqrt{0.4782+0.1741+1.7676+0.0170+0.1026} = \sqrt{2.5395} = \mathbf{1.5936}
$$

d_S4(Q, H1)
$$\Delta = [-0.1197-(-0.9056),\;+1.2860-0.7166,\;-1.6974-(-1.6221),\;+1.4527-(-0.1890),\;+1.5751-1.0134]$$
$$= [+0.7859,\;+0.5694,\;-0.0753,\;+1.6417,\;+0.5617]$$

$$
d_{S4}(Q,H1) = \sqrt{0.6176+0.3242+0.0057+2.6952+0.3155} = \sqrt{3.9582} = \mathbf{1.9896}
$$

d_S4(Q, H2)
$$\Delta = [-0.1197-0.8111,\;+1.2860-1.0001,\;-1.6974-(-0.1890),\;+1.4527-1.8112,\;+1.5751-1.4144]$$
$$= [-0.9308,\;+0.2859,\;-1.5084,\;-0.3585,\;+0.1607]$$

$$
d_{S4}(Q,H2) = \sqrt{0.8664+0.0817+2.2753+0.1285+0.0258} = \sqrt{3.3777} = \mathbf{1.8379}
$$

d_S5(Q, H1)
$$\Delta = [+0.0292-(-0.9865),\;+1.2166-0.2780,\;-1.0248-(-1.2645),\;+1.7338-(-0.7085),\;+1.4899-0.3932]$$
$$= [+1.0157,\;+0.9386,\;+0.2397,\;+2.4423,\;+1.0967]$$

$$
d_{S5}(Q,H1) = \sqrt{1.0316+0.8810+0.0575+5.9648+1.2027} = \sqrt{9.1376} = \mathbf{3.0229}
$$

d_S5(Q, H2)
$$\Delta = [+0.0292-0.6323,\;+1.2166-1.3408,\;-1.0248-(-0.7085),\;+1.7338-1.9731,\;+1.4899-1.8965]$$
$$= [-0.6031,\;-0.1242,\;-0.3163,\;-0.2393,\;-0.4066]$$

$$
d_{S5}(Q,H2) = \sqrt{0.3637+0.0154+0.1000+0.0573+0.1653} = \sqrt{0.7017} = \mathbf{0.8377}
$$

Step B.4 — Categorical S6 Hamming Distance
Intuition: For categorical flags, a value of "has CJK" is not 10% different from "doesn't have CJK" — it is entirely different and has discrete consequences for model selection. Normalised Hamming distance counts binary mismatches, treating any difference $>0.5$ as a flag disagreement. Code: mkb_similarity.py:397-418.

Formula:

$$
d_{\text{cat}}(Q,H) = \frac{1}{|\mathcal{K}|}\sum_{k \in \mathcal{K}} \mathbf{1}\!\left[|Q_k - H_k| > 0.5\right]
$$

Substitution — Q vs H1 (17 keys total):

| Key | Q | H1 | $|Q-H|$ | Disagrees? |
|---|---|---|---|---|
| cat__n_languages | 3 | 2 | 1 | YES |
| cat__n_tonal | 1 | 0 | 1 | YES |
| cat__has_tonal | 1 | 0 | 1 | YES |
| cat__n_script_types | 2 | 1 | 1 | YES |
| cat__has_cjk | 1 | 0 | 1 | YES |
| cat__has_latin | 1 | 1 | 0 | no |
| cat__n_isolating | 1 | 0 | 1 | YES |
| cat__n_polysyllabic | 2 | 2 | 0 | no |
| cat__n_language_families | 3 | 2 | 1 | YES |
| cat__frac_germanic | 0.333 | 0.5 | 0.167 | no |
| cat__frac_romance | 0.333 | 0.5 | 0.167 | no |
| all others | 0 | 0 | 0 | no |

$$n_{\text{diff}} = 7, \quad |\mathcal{K}| = 17$$

$$d_{\text{cat}}(Q,H1) = \frac{7}{17} = \mathbf{0.4118}$$

Substitution — Q vs H2:

| Key | Q | H2 | $|Q-H|$ | Disagrees? |
|---|---|---|---|---|
| cat__n_languages | 3 | 2 | 1 | YES |
| cat__n_tonal | 1 | 1 | 0 | no |
| cat__has_tonal | 1 | 1 | 0 | no |
| cat__n_script_types | 2 | 2 | 0 | no |
| cat__has_cjk | 1 | 1 | 0 | no |
| cat__n_isolating | 1 | 1 | 0 | no |
| cat__n_polysyllabic | 2 | 1 | 1 | YES |
| cat__n_language_families | 3 | 2 | 1 | YES |
| cat__frac_romance | 0.333 | 0.0 | 0.333 | no |
| all others | match | match | 0 | no |

$$n_{\text{diff}} = 3, \quad |\mathcal{K}| = 17$$

$$d_{\text{cat}}(Q,H2) = \frac{3}{17} = \mathbf{0.1765}$$

Step B.5 — Weighted Composite Distance
Intuition: Not all strata are equally informative. The weighted composite distance averages the six per-stratum distances using stratum-specific weights. With equal weights the formula reduces to a plain mean. Code: mkb_similarity.py:422-445, SimilarityEngine._weighted_distance().

Formula:

$$
D(Q, H) = \frac{\displaystyle\sum_{s} w_s \, d_s(Q, H)}{\displaystyle\sum_{s} w_s}
$$

Substitution — Q vs H1 (all $w_s = 1.0$):

Stratum	$d_s$	$w_s$	$w_s \times d_s$
S1_morphological	2.8810	1.0	2.8810
S2_lexical_diversity	2.4514	1.0	2.4514
S3_structural	2.5897	1.0	2.5897
S4_info_theoretic	1.9896	1.0	1.9896
S5_cross_level	3.0229	1.0	3.0229
cat (S6)	0.4118	1.0	0.4118
Sum		6.0	13.3464
$$D(Q, H1) = \frac{13.3464}{6.0} = \mathbf{2.2244}$$

Substitution — Q vs H2:

Stratum	$d_s$	$w_s \times d_s$
S1	1.0126	1.0126
S2	1.2585	1.2585
S3	1.5936	1.5936
S4	1.8379	1.8379
S5	0.8377	0.8377
cat	0.1765	0.1765
Sum		6.7168
$$D(Q, H2) = \frac{6.7168}{6.0} = \mathbf{1.1195}$$

Similarity percentages (code: mkb_similarity.py:526-528):

$$D_{\max} = \max(2.2244,\;1.1195) = 2.2244$$

$$\text{sim}_{H1} = \left(1 - \frac{2.2244}{2.2244}\right) \times 100 = \mathbf{0.0\%}$$

$$\text{sim}_{H2} = \left(1 - \frac{1.1195}{2.2244}\right) \times 100 = \left(1 - 0.5032\right)\times 100 = \mathbf{49.7\%}$$

Top-$k$ sorted ($k=2$): H2 (D=1.1195, sim=49.7%) → H1 (D=2.2244, sim=0.0%)

Step B.6 — Inverse Distance Weighting (IDW) Model Voting
Intuition: Closer historical datasets should carry more influence on the recommendation. IDW assigns each dataset a weight of $1/D$ so that H2 (nearly 2× closer than H1) exerts proportionally more influence. Each model variant accumulates weighted votes scaled by its benchmark score on that dataset. Code: mkb_similarity.py:541-609, SimilarityEngine._idw_vote().

Formula:

$$
\text{score\_raw}(m) = \sum_{i=1}^{k} \frac{1}{D_i + \varepsilon} \cdot f_1(m, H_i) \cdot c(m, H_i)
$$

$$
\text{score\_norm}(m) = \frac{\text{score\_raw}(m)}{\displaystyle\sum_{i=1}^{k} \frac{1}{D_i + \varepsilon}}
$$

where $c(m, H_i) = 1.0$ (no language coverage penalty in this example, no user_iso_codes filter applied at vote time in the default path), and $\varepsilon = 10^{-9}$.

Substitution:

$$
\frac{1}{D_{H1}} = \frac{1}{2.2244} = 0.4496, \qquad \frac{1}{D_{H2}} = \frac{1}{1.1195} = 0.8932
$$

$$
\Sigma_{\text{inv}} = 0.4496 + 0.8932 = 1.3428
$$

Model A (fasttext_word, scores: H1→0.82, H2→0.75):

$$
\text{raw}(A) = 0.4496 \times 0.82 + 0.8932 \times 0.75 = 0.3687 + 0.6699 = 1.0386
$$

$$
\text{norm}(A) = \frac{1.0386}{1.3428} = \mathbf{0.7735}
$$

Model B (tfidf_lr, scores: H1→0.79, H2→0.88):

$$
\text{raw}(B) = 0.4496 \times 0.79 + 0.8932 \times 0.88 = 0.3552 + 0.7860 = 1.1412
$$

$$
\text{norm}(B) = \frac{1.1412}{1.3428} = \mathbf{0.8499}
$$

Result:

$$\text{score\_norm}(B) = 0.8499 > \text{score\_norm}(A) = 0.7735$$

$$\boxed{\text{Recommended model} = \texttt{tfidf\_lr} \quad (\text{Model B})}$$

Step B.7 — Confidence Score
Intuition: The confidence measures neighbour consensus — if all $k$ neighbours agree on the winning model, we are confident; if they split, the recommendation is weaker. Code: mkb_similarity.py:168-170.

Formula:

$$
\text{confidence} = \frac{\text{number of top-}k\text{ neighbours whose best\_model} = \hat{m}}{k}
$$

Substitution:

H2's best model (by f1_macro): $\max(0.75, 0.88) = 0.88$ → Model B ✓
H1's best model: $\max(0.82, 0.79) = 0.82$ → Model A ✗
$$n_{\text{agree}} = 1 \quad (H2\text{ only}), \quad k = 2$$

$$\text{confidence} = \frac{1}{2} = \mathbf{0.50} \; (50\%)$$

Summary — Complete Numerical Pipeline
Stage	Operation	Key Output
A.1	Stratum assignment (first-match)	5 strata × 2 features each
A.2	StandardScaler per stratum	$\mu, \sigma$ vectors stored in StratumFit.scaler
A.3	PCA per stratum	1 PC retained per stratum ($\geq$99% variance); $\mathbf{v}_1$ stored in StratumFit.pca
A.4	Aggregate statistics per PC	5 stats × 1 PC × 5 strata = 25-dim continuous block
A.5	Typology flags	17-dim categorical S6 block; total fingerprint = 42 dims
B.1	Transform Q through saved scaler + PCA	Q PC scores per language per stratum
B.2	Aggregate Q stats	Q fingerprint (42 dims)
B.3	Euclidean per stratum	$d_{S1}$–$d_{S5}$: Q closer to H2 on all strata
B.4	Normalised Hamming on cat__*	$d_{\text{cat}}(Q,H1)=0.41$ vs $d_{\text{cat}}(Q,H2)=0.18$
B.5	Weighted composite $D$	$D(Q,H1)=2.224$, $D(Q,H2)=1.120$
B.6	IDW vote	norm(B)=0.850 > norm(A)=0.774 → tfidf_lr
B.7	Confidence	50% (1/2 neighbours agree)
Why H2 consistently dominates: Q contains zh — a tonal, CJK, isolating language. H2 also contains zh, so its fingerprint encodes the wide morphological/entropy spread that zh introduces (high $\sigma_0$, extreme min/max on all strata). Q's fingerprint inherits that same shape. H1 (en+es only) is uniformly in the "morphologically-rich, low-entropy, cohesive" quadrant of all five strata — a poor match.

Why Model B wins despite H1 preferring Model A: H2 (the closer neighbour) gets weight $0.893$ vs H1's $0.450$ — a 2:1 ratio. Even though Model A performs slightly better on H1 (0.82 vs 0.79), Model B's advantage on the heavily-weighted H2 (0.88 vs 0.75) dominates the aggregation. This is the core IDW mechanism: proximity amplifies the nearer dataset's vote.
