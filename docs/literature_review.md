# Estimating Communication Accuracy from Network-Structural Signals: A Literature Review and Research Program

*Working document. Compiled 2026-05-07.*

---

## 0. Origin and Scope

This review was produced to map the existing literatures bearing on the question: **given an intercepted communication of partly-known origin, can we estimate the likelihood that it is accurate using network-structural signals — and can we calibrate such an estimator in a controlled laboratory of LLM-powered agents?**

Six literatures speak to pieces of this question. None occupies the full intersection. The body of this review walks through each, reports its load-bearing works, and locates the gap that the proposed program would fill.

The thread-level bibliographies (Section 9) contain ~180 distinct citations with verified venues and direct links. Inline citations in Sections 1–8 are selective; the appendix is for depth.

---

## 1. The Problem and Framing

The question, in receiver-centered form: a node in some communication system receives a message. The receiver has access to some subset of the available evidence about that message — its content, partial information about how it traveled, partial knowledge of the network it traveled through, perhaps some metadata about the source. Given that information set, what can the receiver infer about the message?

The construct is general. Receivers in different domains — intelligence analysts, scientists evaluating a citation chain, employees parsing an organizational rumor, social-media users encountering a viral claim, criminals or insurgents on the receiving end of an intercepted-and-relayed report — differ chiefly in their information sets and their rationality assumptions. Both of those are experimental treatments in the framework that follows.

### 1.1 Three estimands, not one

Three distinct quantities need to be separated upfront, because the existing literatures routinely collapse them:

- **Accuracy** — does the message correspond to the underlying state of the world?
- **Fidelity** — does the received message preserve the original message that was sent?
- **Provenance** — where in the network did the message originate, and how did it travel?

These come apart cleanly. A message can be high-fidelity and inaccurate (the original was wrong; transmission preserved it). Low-fidelity but accurate (the original was wrong; downstream nodes corrected it). From a structurally reliable network and still false (the source's perception of the world was incorrect). From an adversarial node and still accurate (a strategic actor tells the truth instrumentally). The disinformation literature conflates these; the receiver-centered framework keeps them apart.

### 1.2 The generative model

The natural generative chain underlying any received message is:

```
World W  →  Source observation S(W)  →  Initial message M₀
        →  Network propagation (G, H)  →  Received message M_i
```

`G` is the generating topology, `H` is the traversal history through it, `M_i` is what the receiver observes. Each arrow can carry noise; each can be adversarially perturbed. The three estimands map onto different segments of the chain: *fidelity* studies `M₀ → M_i`; *accuracy* additionally couples to `S(W) → M₀`; *provenance* asks the receiver to invert `(G, H) → M_i` partially or fully.

This separation organizes the project. *Fidelity* is the cleanest first object because `M₀` is observable to the experimenter even when it is hidden from the receiver — ground truth is direct. *Accuracy* requires unfreezing the `S(W)` arrow (modeling source perceptual error and bias). *Provenance* is partly identifiable from message content alone, partly from path/timing, and partly only with explicit network knowledge.

### 1.3 The receiver as a research-design parameter

The receiver is not a parameter-free inference engine. Two receivers with the same information set will produce different posteriors depending on their priors and reasoning. The framework must commit to one — or, more interestingly, compare across — three idealizations:

- **Optimal Bayesian receiver** — analytic upper bound on what any receiver could infer from the information set. Theoretically clean, unrealistic in practice.
- **Bounded-rational statistical receiver** — a classifier or regressor trained on simulated data. Achievable in practice; sensitive to feature engineering and training distribution.
- **LLM receiver** — produces explicit probability judgments. Most "human-like" but carries the algorithmic-fidelity, machine-bias, and RLHF-truthful-prior risks documented in §2.6.

The gap between these is itself a finding. The optimal-Bayesian ceiling tells you what is *in principle* recoverable from a given information set; the statistical receiver tells you what is *practically* recoverable; the difference quantifies the inferential cost of bounded rationality.

### 1.4 Information set as experimental treatment

Rather than holding "what the receiver knows" constant, the design varies it systematically. The matrix of information regimes (content only / content + domain priors / content + local topology / content + path metadata / content + mutation history / full graph) crossed with the three estimands becomes the empirical core of the project. The research question, technically:

> Under experimentally varied information regimes `I_k`, can receiver nodes produce calibrated estimates of `Pr(A | I_k)`, `Pr(F | I_k)`, and `Pr(G, O, H | I_k)`, and how do these estimates degrade under semantic mutation, sparse observation, and adversarial spoofing?

### 1.5 Per-target identifiability as theoretical scaffolding

Some inferential targets should be more identifiable than others, and stating this upfront keeps the empirical matrix from being a fishing expedition. Plausible orderings:

- *fidelity* > *accuracy* under a fixed source (fidelity needs only `M₀`; accuracy needs `W`).
- *origin class* > *exact origin* (core/periphery/broker/hub may be recoverable when the exact source node is not).
- *transmission regime* (chain / broadcast / redundant-path / clustered reinforcement) > *full topology recovery*.

Where these orderings hold and where they break is part of what the experiment establishes.

### 1.6 Single-message versus stream

A receiver who sees one message at one intercept point is solving a different problem from one who updates across multiple messages or multiple intercepts of the same message. The first paper should treat the single-message case; sequential and multi-intercept receivers are natural sequels. Stating this scope explicitly forecloses the predictable reviewer question.

### 1.7 Adversarial robustness as a primary design criterion

Any structural-signal-based receiver-side inference faces an arms race. A sophisticated adversary who knows the receiver's inference procedure can spoof its inputs. The cost of spoofing — how expensive evasion is at scale, and which structural features are intrinsically expensive to spoof versus cheaply mimicked — becomes a central design criterion, not an afterthought. This concern shapes Inquiry IV in §4 and is grounded in the disinformation literature reviewed in §2.5.

---

## 2. Six Literatures

### 2.1 Topology and information accuracy (the forward problem)

The forward problem — how does network structure shape what gets through — is the most mature of the six literatures. Six broad findings have substantial cross-method support.

**(i) Topology shapes diffusion holding individual behavior fixed.** Centola's clean experimental design (Centola 2010, *Science*) demonstrates that two networks with identical degree distributions but different clustering produce different cascades. Watts (2002, *PNAS*) gives the analytical basis; Vosoughi, Roy, and Aral (2018, *Science*) provide the largest-scale empirical demonstration: across ~126,000 cascades, falsehoods diffused farther, faster, deeper, and more broadly than truths, with topology-specific signatures.

**(ii) Simple and complex contagions behave oppositely with respect to long ties.** Centola and Macy (2007, *AJS*) inverted Granovetter's "strength of weak ties" intuition for high-threshold information: long bridges accelerate single-exposure contagions but impede multi-exposure ones. Romero, Meeder, and Kleinberg (2011, WWW) showed empirically on Twitter that political hashtags exhibit complex-contagion signatures while idioms exhibit simple-contagion ones. *Contagion type is content-specific* — a fact that any inverse-inference estimator must accommodate.

**(iii) More connectivity is not monotonically better for accuracy.** The Zollman effect (Zollman 2007, *Phil Sci*) — that less-connected scientific communities sometimes converge on truth more reliably than more-connected ones — generalizes to the Lazer–Friedman inverted U (2007, *ASQ*) and to Golub–Jackson's "prominent group" obstruction to wisdom-of-crowds (2010, *AEJ:Micro*). Becker, Brackbill, and Centola (2017, *PNAS*) qualified the picture with experimental evidence that *decentralized* (egalitarian) influence improves numerical-estimation accuracy. Mason and Watts (2012, *PNAS*) found efficient networks helped on parameter-search problems. The reconciliation appears task-dependent and remains theoretically open.

**(iv) Falsehood spreads farther/faster/deeper than truth, in the open-platform regime.** Vosoughi, Roy, and Aral (2018) is canonical; Friggeri et al. (2014, ICWSM) and Del Vicario et al. (2016, *PNAS*) align. The mechanism is contested — novelty, affect, identity-signaling, or some mixture — but the structural signature is robust.

**(v) Echo chambers exist but are smaller and more concentrated than popular discourse implies.** Bakshy, Messing, and Adamic (2015, *Science*); Flaxman, Goel, and Rao (2016, *POQ*); Guess, Nyhan, and Reifler (2020, *Nature Human Behaviour*); and Cinelli et al. (2021, *PNAS*) collectively show that homophily exists, that algorithmic curation contributes additively but modestly, and that platform design substantially moderates the effect.

**(vi) Serial reproduction systematically distorts content.** Bartlett (1932) is foundational; Mesoudi and Whiten (2008, *Phil Trans B*), Kashima (2000, *PSPB*), and Acerbi and Stubbersfield (2023, *PNAS*) — the last using LLMs as transmission agents — establish that content drifts toward gist, schema, stereotype, and emotional salience. Importantly: *Acerbi and Stubbersfield show LLMs exhibit the same content biases as human transmission chains*, which is a positive existence proof for using LLMs as proxies in transmission studies.

**Open in this literature:** very little work jointly models cascade shape *and* content mutation. Rumor models (Daley–Kendall 1965; Maki–Thompson 1973; Moreno, Nekovee, and Pacheco 2004) treat the propagated item as an unchanging token. The transmission-chain tradition tracks mutation but only on linear chains. Vosoughi, Roy, and Aral predict reach, not truth-status from structure. Whether one can predict the *truthfulness* of a message from structural signatures of its propagation (cascade depth, breadth, reshare delay, mutation rate) is genuinely open. This gap appears in nearly identical form in Section 2.2 below — it is the central seam of the literature.

### 2.2 Inverse inference: source and structure from signal

The inverse problem splits into three sub-literatures that, together, define a triangular gap.

**(a) Source localization on known graphs.** Single-source detection on a known graph from a snapshot is well-understood. Shah and Zaman (2011, *IEEE Trans IT*) introduced rumor centrality; Pinto, Thiran, and Vetterli (2012, *PRL*) developed the observer-based formulation that maps most directly onto intelligence-intercept settings (a sparse set of nodes report receipt times). Zhu and Ying (2016) handled the SIR (recovery) variant; Lokhov, Mézard, Ohta, and Zdeborová (2014, *PRE*) introduced dynamic message-passing, which is the most extensible framework for partial observations and joint estimation. Prakash, Vreeken, and Faloutsos (2014) handle multiple sources via MDL. Jiang, Wen, Yu, Xiang, and Zhou (2017, *IEEE Comms Surveys*) is the canonical survey. **All assume the graph is given.**

**(b) Network inference from cascade timing.** Gomez-Rodriguez, Leskovec, and Krause's NetInf line (2010 KDD; 2011 ICML; 2014 JMLR sample-complexity bounds) recovers an underlying directed graph from many cascades' timing observations. Lokhov and Misiakiewicz (2015) reconstruct *both* topology and edge weights from partial cascade observation. Peixoto (2019, *PRL*; 2025, *Phys Rev X*) provides the Bayesian/MDL framework for joint reconstruction of structure and community. **All use timing as the inferential signal; content is treated as an opaque event.**

**(c) Stylometry, authorship attribution, and computational sociolinguistics.** Mosteller and Wallace (1964) is the foundation; Stamatatos (2009, *JASIST*) and Juola (2008) the modern surveys. Argamon, Koppel, Pennebaker, and Schler (2009, *CACM*) demonstrate that text leaks demographic and social-position attributes — age, gender, native language — at 75–90% accuracy. Abbasi and Chen's Writeprints (2008, *ACM TOIS*) achieves 94% on 100-author cybercrime corpora. Brennan, Afroz, and Greenstadt (2012) document adversarial stylometry as a robustness limit. Nguyen, Doğruöz, Rosé, and de Jong (2016, *Comp Ling*) survey computational sociolinguistics. Bramsen et al. (2011, ACL) extract superior-subordinate language patterns from Enron. Diesner and Carley's CASOS-line work extracts named-entity meta-matrices from text. **All treat the message individually or extract author attributes; none infers the propagation network from message content.**

The triangular gap: there is no principled framework where *p(network | observations)* couples a propagation likelihood (from timing/structure) with a stylometric likelihood (from message content). The closest precedents — Lokhov–Misiakiewicz (joint topology + transmission probability from timing); Newman and Clauset (2016, *Nat Commun*) on joint community-and-attribute inference — point toward the framework but do not occupy the corner. Linder, Desmarais, et al. (2020, *Data & Policy*) is one of very few papers explicitly attempting "infer a network from text alone" and finds that it yields content-similarity networks, *not* social/propagation networks. The user's specific question — *jointly infer originating network topology AND message trustworthiness from intercepted messages plus partial structural observation* — is genuinely unaddressed.

### 2.3 Dark and covert networks

The dark-networks literature is the natural applied domain and provides a critical theoretical scaffold.

The foundational empirical works — Sparrow (1991, *Social Networks*); Krebs (2002, *Connections*); Baker and Faulkner (1993, *ASR*) — established that illegal networks are shaped by a **secrecy–efficiency tradeoff**. Baker and Faulkner's analysis of three price-fixing conspiracies showed that the more decentralized, harder-to-detect networks survived legal action better than centralized ones; the cost was operational inefficiency. Crossley, Edwards, Harries, and Stevenson (2012, *Social Networks*) corroborated longitudinally with the UK suffragettes: as repression rose, density and centralization fell. Lindelauf, Borm, and Hamers (2009, *Social Networks*) derived this formally — optimal covert communication graphs are *not* small-world; they trend toward stars or paths under joint detection-risk and information-utility penalties. Enders and Su (2007, *JCR*) predicted, before confirmation, that post-9/11 al-Qaeda would flatten and decentralize.

The book-length treatments (Everton 2012; Cunningham, Everton, and Murphy 2016; Morselli 2009 *Inside Criminal Networks*) consolidate the field. Carley's CMU/CASOS line (Carley 2006, *CMOT*; Diesner and Carley 2005) develops dynamic network analysis treating covert organizations as evolving meta-networks of people × knowledge × resources × tasks.

The communication-side — what dark networks *say* and how it appears when intercepted — is less developed but pivotal for the proposed program. Stohl and Stohl (2007, *Communication Theory*; 2011, *Organization Studies*) develop the "communicative constitution of clandestinity": secrecy is not the absence of signal but a structured signaling regime. Carson (2017) on covert communication in international relations argues that covert messages *are* designed to be intelligible to insiders while signaling resolve to adversaries. Natarajan (2006) on conversational analysis of drug-traffic phone calls is one of the rare empirical uses of intercepted-message *content* for structural inference.

Stylized communication facts emerging from this literature: dark-network messages tend to be **shorter and less elaborated**; **euphemistic or pre-coded** with substituted referents; **redundant in safety-critical respects but sparse in routine information**; **asymmetric in role-use of language** (brokers compress, principals avoid direct content); **bursty rather than continuous**. These are precisely the features a content-conditioned structural estimator might exploit.

The literature acknowledges its own gap. Nearly all SNA on dark networks treats the intercept as ground-truth — the wiretap *is* the network, modulo missing-data correction. Yet Stohl and Stohl, Carson, and Morselli all emphasize that covert actors strategically degrade the informativeness of their messages. Quantitative models of how *much* signal survives, conditional on tie strength, role, and risk environment, are absent. The endogenous coupling of structure and content is not modeled in any extant framework. Recent computational work (Berlusconi et al. 2016; Cavallaro et al. 2020; Ficara et al. 2022) on link prediction in criminal networks uses structure only — joint structure-plus-content models conditioned on per-message accuracy could yield substantial gains.

### 2.4 Intelligence analysis, credibility, and deception

Five sub-communities populate this space, and they cite each other unevenly.

**(a) Structured analytic techniques.** Heuer's *Psychology of Intelligence Analysis* (1999) is the canonical text; Heuer and Pherson's *Structured Analytic Techniques for Intelligence Analysis* (3rd ed. 2019) the operational catalogue. Analysis of Competing Hypotheses (ACH) — originally developed by Heuer for Reagan-era Soviet deception courses — is the field's closest thing to a formal evidential calculus, explicitly aimed at deception scenarios. Procedural and prose-based; suspicious of formal probability.

**(b) Behavioral-decision and forecasting.** Sherman Kent's "Words of Estimative Probability" (1964) framed the verbal-vs-numeric debate that still structures the field. Mandel and Barnes (2014, *PNAS*) provide the empirical anchor: 1,514 strategic-intelligence forecasts over six years showed good discrimination and calibration but systematic underconfidence. Friedman and Zeckhauser (2012, 2015, *Intelligence and National Security*) distinguish *likelihood* from *confidence* and argue numeric or numeric-anchored verbal probabilities outperform pure verbal ones. Tetlock and Gardner (2015) and the IARPA ACE / Good Judgment Project results (Mellers, Stone, Atanasov, et al. 2014, 2015) establish that trained-and-aggregated forecasters reach Brier scores of ~0.20 on geopolitical questions, beating IC baselines.

**(c) Forensic deception psychology.** Bond and DePaulo's meta-analysis (2006, *PSPR*) — 206 studies, 24,483 judges, 54% accuracy on lie-vs-truth without aids — sets the empirical baseline. DePaulo et al.'s 158-cue meta-analysis (2003, *Psychological Bulletin*) is the "no Pinocchio's nose" finding. Vrij (2008) is the standard reference; Vrij, Granhag, and Mann (2011, *Current Directions*) shifted the field toward active interview techniques (cognitive load, Strategic Use of Evidence). Foundational concepts: Reality Monitoring (Johnson and Raye 1981), CBCA (Steller and Köhnken 1989).

**(d) Computational deception and NLP.** Newman, Pennebaker, Berry, and Richards (2003, *PSPB*) — the LIWC fingerprint of deception (fewer first-person singulars, fewer exclusive words, more negative emotion, less cognitive complexity — ~67% accuracy when topic is held constant). Hancock et al. (2008, *Discourse Processes*) extended to CMC, finding that synchronous-chat liars use *more* words and other-references — *deception linguistics is medium-dependent*. The post-2018 deep-learning explosion has produced higher-accuracy classifiers but with worse cross-domain generalization.

**(e) Game-theoretic communication.** Crawford and Sobel (1982, *Econometrica*) — the founding cheap-talk paper. Equilibria are partition equilibria; the closer sender and receiver preferences, the finer the partition (more information transmitted). Kamenica and Gentzkow (2011, *AER*) on Bayesian persuasion: when the sender has commitment, the *distribution* of messages is informative. Bergemann and Morris (2019, *JEL*) survey information design as a unified problem. **The receiver-side reading of Bayesian persuasion is essentially the operator's framing in the user's project.**

A sixth, smaller community — **evidential Bayesian networks** (Schum 1994; Kadane and Schum 1996; Tecuci, Schum, Marcu, and Boicu 2016) — is the only group explicitly bridging formal probability and messy real-world evidence. They cite SAT and the legal-evidence literature heavily; cited only weakly back.

The cross-citation pattern matters: the intelligence-studies journals (*Intelligence and National Security*, *Studies in Intelligence*) host (a)–(b); psychology journals host (c); NLP venues host (d); economics journals host (e). They essentially do not co-cite. **There is no established lab combining game-theoretic communication models with empirical deception linguistics on closed-network intercepted communications.**

What an operator can already use from this literature: calibration baselines (Mandel/Barnes; Tetlock); two-axis source/info reliability scales (NATO Admiralty Code A1–F6); lossy verbal-probability conventions (Kent; Friedman & Zeckhauser); aggregation-beats-individuals (GJP); LIWC fingerprints with ~60–67% ceilings and sharp context dependence; Bayesian-network evidence aggregation (Schum/Kadane). What is missing: any of these calibrated against *network-structural* signals; any of them tested on *intercepted* (third-person, closed-network) communications; any principled bridge between cheap-talk theory's predicted partition equilibria and observed deception linguistics.

### 2.5 Disinformation and adversarial dynamics

This literature defines the threat model for any network-structural estimator. Several network-level signatures of inauthentic operations recur in the literature:

- **Temporal synchronization** (Pacheco et al. 2021, ICWSM; Giglietto et al.'s CooRnet 2020, *ICS*).
- **Behavioral-trace similarity graphs** — shared hashtags, URLs, retweets, follower sets, images forming dense subgraphs (Pacheco et al. 2021).
- **Cascade topology asymmetries** (Vosoughi, Roy, and Aral 2018) — false news is structurally distinctive.
- **Superspreader concentration** — Grinberg et al. (2019, *Science*): 0.1% of users shared 80% of fake news during 2016.
- **Cross-platform laundering pathways** (Yang et al. 2021; Starbird 2017).
- **Account-feature anomalies** (Botometer; Davis et al. 2016).
- **Stylometric homogeneity in persona networks** (Kumar et al. 2017).

Each signature has a known evasion vector. Cresci's *A Decade of Social Bot Detection* (2020, *CACM*) is the field's blunt assessment: no technological advance has produced a durable defender's advantage over the past decade. The cycle — detect, evade, redetect, re-evade — has produced ratchet dynamics that favor the adversary, especially as:
- public-detector exposure invites Goodhart's-law optimization against published features;
- generalization gaps mean each new operation is partially out-of-distribution (Yang et al. 2020; Cresci et al. 2025);
- graph-level adversarial attacks are budget-cheap (Zügner et al. 2018, KDD; Bojchevski and Günnemann 2019, ICLR);
- LLMs lower per-persona cost of high-quality content by orders of magnitude (Goldstein et al. 2023, SIO).

Starbird's "participatory disinformation" framing (Starbird, Arif, and Wilson 2019, *PACMHCI*; Starbird, DiResta, and DeButts 2023, *Social Media + Society*) further complicates detection: organic-but-misleading and inauthentic-and-coordinated activity are structurally entangled, so detectors that rely on inauthenticity signatures systematically misclassify hybrids.

For the present project, the most consequential gap in this literature is: **there is essentially no published empirical work on the cost to an adversary of evading a given network-structural signal at scale**, and **no published work specifically tests adversarial attacks on rumor-source-localization estimators**. Most academic detectors operate on one platform; real operations are cross-platform. Most work conflates "low accuracy" with "deception"; honest-but-noisy senders have different network signatures from high-effort deception operations, and that distinction is largely undeveloped.

### 2.6 LLM-powered agent-based models

This is the youngest, fastest-moving, and most relevant of the six literatures.

The foundational work is Park, O'Brien, Cai, Morris, Liang, and Bernstein (2023, UIST) — *Generative Agents* established the memory/reflection/planning architecture that defines the field. Park et al. (2024, arXiv) — *Generative Agent Simulations of 1,000 People* — sets the current state of the art on individual-level fidelity, with agents reproducing real-participant GSS responses at 85% of test-retest reliability when grounded in two-hour interviews. Argyle, Busby, Fulda, Gubler, Rytting, and Wingate (2023, *Political Analysis*) coined "algorithmic fidelity"; Aher, Arriaga, and Kalai (2023, ICML) replicated Ultimatum Game, Milgram, and other classics; Horton, Filippas, and Manning (2023, NBER; *EC '24*) showed economic-experiment replication.

For the user's question, the directly relevant subset is:
- **Tornberg, Valeeva, Uitermark, and Bail (2023)** — 500-LLM-persona simulated Twitter testing feed-algorithm effects on cross-partisan exposure.
- **Chuang, Goyal, Harlalka, et al. (2024, *Findings of NAACL*)** — opinion dynamics on networks of LLM agents; documents a strong "truthful" RLHF-induced prior that must be counteracted with explicit confirmation-bias prompts to recover classical fragmentation.
- **Liu et al. (2024, arXiv:2410.13909)** — *News Diffusion Under Different Network Structures*: directly varies network topology (random, small-world, scale-free) for LLM-agent news spread. **The closest existing work to the user's project, but treats news as a discrete state, not text whose semantic content can mutate.**
- **Li et al. (2024, EMNLP 2025)** — *FUSE / Stepwise Deception*: explicitly models semantic drift of true news into fake news through paraphrase and commentary. **Does not vary network topology — drift is the focus, network is fixed.**
- **Lu et al. (2025, COLING)** — echo-chamber simulations across topologies; opinions treated as scalars/labels, not text.
- **Acerbi and Stubbersfield (2023, *PNAS*)** — single-LLM serial reproduction shows the same content biases as human transmission chains. **Linear chain only — no network structure.**
- **Qiu et al. (2025, EMNLP)** — *topology and information propagation in LLM multi-agent systems*: sparse topologies suppress error propagation but block useful information; dense topologies do the opposite. **Engineering framing (which topology completes the task best?), not social science (how does network shape what a message becomes?).**

The methodological state of the art uses Park-style memory architectures, persona prompts grounded ideally in interview data (Park 2024) or at least in survey backstories (Argyle), and validation via behavioral replication, survey replication, or stylized-fact matching. Frameworks in active use: CAMEL/OASIS, AutoGen, AgentVerse, Concordia (DeepMind), AgentSociety (Tsinghua), GenSim. Scale ranges from Park's original 25 agents to OASIS's 1M.

The skeptical literature has crystallized: **machine bias / algorithmic infidelity** (Boelaert et al. 2025, *Sociological Methods & Research*; Bisbee et al. 2024, *Political Analysis*); **caricature** (Cheng, Durmus, and Jurafsky 2023, EMNLP); **homogeneity collapse**; **social-desirability and sycophancy** (Salecha et al. 2024, *PNAS Nexus*); **causal-inference violations** (Wang et al. 2023); **validation circularity** (Larooij and Tornberg 2025, *AI Review*). The "truthful prior / RLHF artifact" — that LLM agents converge to mainstream consensus regardless of starting beliefs — is a structural bias the user's program must explicitly counteract.

**The clear gap.** No published work combines all three of (1) systematic variation in network topology, (2) continuous-text messages whose semantic content can mutate during transmission, and (3) quantitative measurement of message *fidelity* — the semantic distance between origin and downstream messages — as a function of (1). Adjacent work (FUSE, Liu news-diffusion, transmission-chain experiments, Qiu topology-vs-error) demonstrates that the building blocks exist; nobody has assembled them into a topology-vs-semantic-fidelity laboratory.

---

## 3. The Convergent Gap

Five of the six independent reviews converged on the same gap, framed differently each time:

| Literature | Gap as named in that literature |
|---|---|
| Topology & accuracy | "Joint modeling of diffusion shape and content mutation" — cascade-shape work predicts reach, not accuracy. |
| Inverse inference | The triangular gap between source-localization-on-known-graphs, network-inference-from-cascade-timing-only, and stylometry/profiling. No principled framework couples propagation likelihood with stylometric likelihood. |
| Dark networks | Inferring true network structure from observable communication content. Almost all SNA on dark networks treats intercepts as ground truth; content features are unused as inferential signal despite Stohl, Carson, and Morselli all suggesting they should be informative. |
| Intelligence analysis | No empirical work on credibility of intercepted (third-person, closed-network) communications; uncalibrated A1–F6 source scales; cheap-talk theory unconnected to empirical deception detection. |
| Disinformation/adversarial | No published work tests adversarial attacks against network source-localization estimators; the cost-to-evade question is empirically open. |
| LLM-ABM | No work combines topology variation + continuous-text semantic mutation + fidelity measurement. |

These are not six separate gaps — they are six views of the same hole. The shape of the hole, viewed from any angle, is roughly:

> **A receiver-centered framework for estimating message accuracy, fidelity, and structural provenance under systematically varied information sets — calibrated against ground truth in a controlled LLM-ABM laboratory, with semantic mutation explicitly modeled and adversarial robustness as a primary design criterion.**

That is the lane.

---

## 4. Proposed Research Program

The lane is real and largely unoccupied. A defensible research program has the following structure.

### 4.1 Core question

> How does variation in a receiver's information set affect its ability to produce calibrated estimates of message accuracy, fidelity, and structural provenance?

This framing has four properties that recommend it.

- It puts the receiver's epistemic position at the center of the inquiry rather than treating it as an afterthought.
- It makes "what is known" an experimental treatment rather than a fixed assumption.
- It separates accuracy, fidelity, and provenance into distinct estimands, matching the literature's conceptual gaps.
- It produces interpretable findings whether absolute performance is high or low. A clean negative result — "content alone is non-identifying for topology beyond coarse classes; sparse path metadata yields large calibration gains" — is just as publishable as a positive one, because it tells future receivers *what information is worth acquiring*.

### 4.2 Staged plan: three papers organized around the generative chain

The three estimands map naturally onto a staged research plan, indexed by which arrows of the `W → S(W) → M₀ → (G, H) → M_i` chain are unfrozen.

**Paper 1 — Fidelity and provenance under partial observability.** Holds `W` and `S(W)` fixed (the original message `M₀` is the experimenter's ground truth). Studies how receivers infer fidelity (correspondence between `M_i` and `M₀`) and provenance (origin class, transmission regime) as a function of information set. The cleanest first object because ground truth is direct.

**Paper 2 — Accuracy with source perceptual error.** Unfreezes `S(W)`. The source observes the world imperfectly, then transmits. Receivers estimate accuracy (correspondence between `M_i` and `W`), which couples fidelity to the source's relationship to world-state.

**Paper 3 — Adversarial spoofing.** Unfreezes adversarial control of intermediate nodes — nodes that know the receiver's inference procedure and deliberately perturb the structural fingerprint. Studies the cost-of-evasion question.

The first paper is the most tractable and the most reviewer-defensible; papers 2 and 3 follow naturally only after the paper 1 evidentiary base exists.

### 4.3 LLM-ABM as a controlled observability laboratory

The methodological commitment is not "LLMs as humans-in-silicon." Its scientific value is that the experimenter knows the latent variables a real receiver typically lacks: the true origin, the graph, the path, the original message, where mutation occurred, and (in paper 2 onwards) the world-state. The experimenter can then *hide different subsets of those variables* from the receiver and observe how inference degrades.

In the paper 1 design, LLMs are used as **controlled semantic transformation engines** — repeated, instrumented, stochastic message rewriters whose mutation behavior can be conditioned on agent traits and structural position. They are *not* used as receivers in paper 1; the receiver is a statistical model (or an explicit Bayesian inference procedure). This hybrid design separates the substantive contribution (the inferential framework) from the LLM black box (a single, replaceable mutation module). LLM-receivers are reserved for follow-up work where comparison to bounded-rational statistical receivers becomes the research object in its own right.

Standard LLM-ABM cautions apply (mixed model families to reduce shared-prior contamination; explicit counter-prompts for the RLHF truthful prior; persona grounding in interview-derived backstories where possible; multiple validation benchmarks against published serial-reproduction and cascade-shape findings). These are detailed in §5.

### 4.4 The central artifact: receiver inference matrix

The empirical core of paper 1 is a matrix of **information regimes × inferential targets**, with calibrated performance estimates in each cell.

| Information available to receiver | Fidelity | Origin class | Exact origin | Transmission regime | Generating topology |
|---|---|---|---|---|---|
| Content only | ? | ? | ? | ? | ? |
| Content + domain priors | ? | ? | ? | ? | ? |
| Content + local topology (ego-net, clustering, redundancy) | ? | ? | ? | ? | ? |
| Content + path metadata (timestamps, repeated arrivals, hop count) | ? | ? | ? | ? | ? |
| Content + mutation history (intermediate forms across hops) | ? | ? | ? | ? | ? |
| Full graph + path | upper bound | upper bound | upper bound | upper bound | upper bound |

Each cell reports calibration (does the receiver's stated probability match the empirical frequency at that level?) and discrimination (AUC or analogue). Cells where inference is non-identifiable are explicitly marked. The first paper's contribution is filling this matrix with severe, controlled measurements, and reporting which information increments produce nonlinear calibration gains.

Paper 2 adds *Accuracy* as a sixth column. Paper 3 examines how each cell degrades as a function of adversary effort.

### 4.5 Hypothesis set

Tightened from loose "topology produces accuracy" intuitions into specific, testable claims.

- **H1.** Incremental observability improves calibration nonlinearly. The marginal gain from adding path redundancy to content-only exceeds the marginal gain from adding stylistic features.
- **H2.** Local topology improves provenance more than fidelity. Ego-network structure reveals whether a message arrived through clustered reinforcement or bridge transmission, but is weakly informative about world-correspondence.
- **H3.** Mutation history outperforms terminal-message features. A trace of semantic drift across hops predicts fidelity better than static features of the final message.
- **H4.** Origin-class inference is more identifiable than origin-node inference. Core / periphery / broker / hub class is recoverable under partial information even when the exact origin node is not.
- **H5.** Adversarial spoofing degrades content-based inference before path-based inference. Linguistic style is cheap to imitate; genuine independent path diversity is more expensive to spoof at scale.
- **H6.** Accuracy and provenance estimates decouple under strategic conditions. Knowing a message came from a hierarchy or hub may improve provenance inference without improving accuracy if the originating actor is biased or deceptive.

### 4.6 Experimental conditions and controls

Several conditions and controls are non-optional given the literature's diagnosed risks.

- **Topic × topology factorial.** Same content across topologies; same topology across content classes; paraphrase-controlled versions within each cell. Without this, the classifier may be reading topic, not structure.
- **Adversarial-aware vs. naive threat models.** Paper 1 reports both; paper 3 makes adversary effort the primary independent variable.
- **Multiple semantic-fidelity metrics.** Embedding cosine, entailment direction, propositional preservation, contradiction detection, omission/addition counting, pragmatic-force preservation. No single metric.
- **Mixed LLM model families** for the mutation engine, to prevent disagreement from collapsing into one model's decoding noise.
- **Receiver-type comparison.** At minimum the optimal-Bayesian ceiling and the bounded-rational statistical floor, so the gap between "in principle recoverable" and "practically recoverable" is explicit.
- **Identifiability tests preceding calibration claims.** For each (information regime, target) cell, test whether the conditional distribution of receiver-observable features under different generating processes is statistically distinguishable, before reporting calibration.

---

## 5. Methodological Cautions

Several issues that emerged across the threads warrant explicit handling.

**Calibration vs. discrimination.** Discrimination ("can I separate true from false?") is a weaker bar than calibration ("when I say 70%, is it true ~70% of the time?"). Operators need calibration. The Tetlock/Mandel/Friedman–Zeckhauser literature provides the methodology; ABM is well-suited to producing calibrated training data because ground truth is controlled.

**Identifiability.** If multiple distinct topologies produce statistically indistinguishable message distributions, the inverse problem is non-identifiable and the operator's dashboard reduces to "uncertainty over structures." This must be tested empirically before any classifier is claimed to work.

**Adversarial spoofing of structural fingerprints.** Once any classifier is known, sophisticated adversaries can spoof it. The program must include adversarial-aware training (Cresci et al. 2019) and stress-testing against detector-aware adversaries.

**LLM-ABM artifacts.** Caricature, homogeneity, social-desirability bias, RLHF truthful prior. None is solved; all are mitigable through mixed models, interview-grounded personas, explicit counter-prompts, and triangulated validation.

**Topic confounding.** A classifier that looks like it's reading topology may be reading topic. Paired conditions are non-negotiable.

**Bayesian formula vs. heuristic score.** The exploratory "operator's score" L = w₁S + w₂R + w₃P − E that motivated the inquiry is a heuristic score, not a posterior. The program should commit to producing a *calibrated* score, with calibration empirically validated, and be honest that the relationship to a true Bayesian posterior is approximate.

**Truth as ground-truth, not consensus.** The provocation "truth is a property of the network that accepts it" conflates ground truth with consensus. The operator wants ground truth; consensus is a proxy. The program should preserve the distinction.

---

## 6. Where this sits among active research communities

Closest natural homes:

- **Methodologically:** the **Lokhov–Zdeborová–Peixoto** axis on Bayesian / message-passing network inference, which already handles partial observations and joint estimation, lacks only the content channel. Adjacent: Carley's CASOS lineage, which already extracts meta-matrices from text but does not infer propagation networks per se.

- **For adversarial robustness:** the **Cresci–Ferrara–Menczer** group on bot detection arms races; the **Günnemann** group on adversarial attacks on graph neural networks. No existing collaboration combines these with source-localization.

- **For dark-network application:** **Everton, Carley, Calderoni, Ficara, De Meo** computational covert-network groups; the Stohl/Stohl communicative-constitution thread; Carson's covert-signaling work in IR.

- **For operator-side calibration:** **Mandel** at DRDC Toronto on intelligence forecast accuracy; **Tetlock/Mellers** at Penn on superforecasting; **Lagnado/Fenton** at UCL/QMUL on Bayesian networks for legal/intelligence evidence.

- **For the LLM-ABM laboratory:** **Park/Bernstein/Liang** at Stanford CRFM; **Tornberg** at Amsterdam; **Acerbi/Stubbersfield** for the cultural-evolution / serial-reproduction perspective; **Baronchelli** for emergent conventions; **Gao/Li/Piao** at Tsinghua FIB for scale.

The negative space is informative: there is no group currently bridging (Lokhov-style joint structure-content inference) × (Cresci-style adversarial robustness) × (Park-style LLM-ABM laboratory) × (Mandel-style calibration) × (Stohl-style covert-communication theory). That intersection, viewed sociologically, is the user's lane.

---

## 7. Open Decisions

Several earlier framing decisions are now resolved by the receiver-centered formulation: the construct is general (not bound to intelligence applications); the contribution is a framework, not an artifact; the science precedes any applied translation. The decisions still genuinely open:

1. **Receiver-type commitment for paper 1.** Optimal Bayesian, bounded-rational statistical, LLM-receiver, or comparison across multiple. *Recommended:* optimal-Bayesian as analytic ceiling and statistical-receiver as achievable floor; LLM-receiver as separate follow-up, since it carries its own validity-critique baggage.

2. **Identifiability-first vs. calibration-first thesis.** Two adjacent framings of the paper:
   - *Identifiability-first*: "What can a receiver, in principle, infer from a given information set?" Cleaner mathematically; produces sharper negative results.
   - *Calibration-first*: "What information increments produce nonlinear calibration gains?" More applied; produces actionable findings.
   
   Both are tractable; the choice affects venue. Identifiability-first reads better in computational social science / network science / theoretical CS. Calibration-first reads better in applied epistemology / decision science / forecasting venues.

3. **Domain of empirical illustration.** Even though the construct is general, paper 1 needs a vivid running example. Synthetic rumor scenario; faux-organizational announcement; simulated covert-communication exchange; synthetic news cascade. The choice affects which existing literatures the paper is most legible to, but should not constrain the framework itself.

4. **Paper 2/3 commitment level.** Whether to scope the staged plan publicly in paper 1 (signals research agenda, more ambitious) or write paper 1 as a standalone with the staged plan held privately (more deliverable, less commitment).

5. **Sequential / multi-intercept receivers.** Paper 1 treats single-message receivers, but the framework extends naturally to a receiver who sees multiple intercepts of the same message or a stream of related messages over time. Whether to scope this as paper 1 follow-up or as a parallel branch of the program.

---

## 8. Summary Verdict

The convergence of six independent literature reviews on the same gap — framed differently each time — supports the intuition that there is a real lane. The receiver-centered formulation makes the lane crisp:

> **Under what information conditions can a receiver produce calibrated estimates of (a) message accuracy, (b) message fidelity, and (c) structural provenance, and how do these estimates change with semantic mutation, partial observability, and adversarial spoofing?**

The novel contribution most clearly differentiated from existing work has four components:

1. **The receiver's information set as the primary experimental treatment** — rather than holding observability constant and varying the message or the network, the framework varies what the receiver knows and measures inferential degradation.
2. **Explicit separation of accuracy, fidelity, and provenance** as distinct estimands, none of which the existing literatures isolate cleanly.
3. **LLM agents as controlled semantic transformation engines** (not as receivers in paper 1), used to instrument the mutation channel under known ground truth.
4. **Calibration as the principal evaluation metric**, with per-target identifiability as the principal theoretical contribution.

This formulation:
- Bridges source-localization (Lokhov / Shah-Zaman lineage) with stylometric inference (Stamatatos / Argamon lineage) through the propagation channel.
- Is general enough to subsume intelligence, rumor, organizational, scientific, and social-media settings without committing to any one.
- Avoids overclaiming truth-detection while preserving the substantive question.
- Produces publishable findings whether the result is positive (specific information increments produce calibration gains) or negative (content alone is non-identifying beyond coarse classes; partial-observability bounds quantified).

No existing paper or research group occupies that intersection.

---

## 9. Consolidated Bibliography

Bibliographies are organized by the six threads. Within each, citations are roughly in order of canonical / load-bearing status. Full thread-level reports (with abstracts and links) are available on request.

### 9.1 Topology and information accuracy

Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. *Science*, 359(6380), 1146–1151.
Lazer, D. M. J., et al. (2018). The science of fake news. *Science*, 359(6380), 1094–1096.
Centola, D. (2010). The spread of behavior in an online social network experiment. *Science*, 329(5996), 1194–1197.
Centola, D., & Macy, M. (2007). Complex contagions and the weakness of long ties. *American Journal of Sociology*, 113(3), 702–734.
Centola, D., & Baronchelli, A. (2015). The spontaneous emergence of conventions. *PNAS*, 112(7), 1989–1994.
Centola, D. (2018). *How Behavior Spreads*. Princeton University Press.
Watts, D. J. (2002). A simple model of global cascades on random networks. *PNAS*, 99(9), 5766–5771.
Granovetter, M. (1978). Threshold models of collective behavior. *American Journal of Sociology*, 83(6), 1420–1443.
Romero, D. M., Meeder, B., & Kleinberg, J. (2011). Differences in the mechanics of information diffusion across topics. *WWW '11*.
Friggeri, A., Adamic, L., Eckles, D., & Cheng, J. (2014). Rumor cascades. *ICWSM '14*.
Goel, S., Anderson, A., Hofman, J., & Watts, D. J. (2016). The structural virality of online diffusion. *Management Science*, 62(1), 180–196.
DeGroot, M. H. (1974). Reaching a consensus. *JASA*, 69(345), 118–121.
Golub, B., & Jackson, M. O. (2010). Naïve learning in social networks and the wisdom of crowds. *AEJ:Microeconomics*, 2(1), 112–149.
Bala, V., & Goyal, S. (1998). Learning from neighbors. *Review of Economic Studies*, 65(3), 595–621.
Friedkin, N. E., & Johnsen, E. C. (1990). Social influence and opinions. *Journal of Mathematical Sociology*, 15(3-4), 193–206.
Hegselmann, R., & Krause, U. (2002). Opinion dynamics and bounded confidence. *JASSS*, 5(3).
Deffuant, G., Neau, D., Amblard, F., & Weisbuch, G. (2000). Mixing beliefs among interacting agents. *Advances in Complex Systems*, 3(1-4), 87–98.
Acemoglu, D., Ozdaglar, A., & ParandehGheibi, A. (2010). Spread of (mis)information in social networks. *Games and Economic Behavior*, 70(2), 194–227.
Acemoglu, D., Ozdaglar, A., & Siderius, J. (2024). A model of online misinformation. *Review of Economic Studies*, 91(6), 3117–3162.
Zollman, K. J. S. (2007). The communication structure of epistemic communities. *Philosophy of Science*, 74(5), 574–587.
Zollman, K. J. S. (2013). Network epistemology: Communication in epistemic communities. *Philosophy Compass*, 8(1), 15–27.
O'Connor, C., & Weatherall, J. O. (2019). *The Misinformation Age*. Yale University Press.
Bartlett, F. C. (1932). *Remembering*. Cambridge University Press.
Mesoudi, A., & Whiten, A. (2008). The multiple roles of cultural transmission experiments. *Phil Trans B*, 363(1509), 3489–3501.
Kashima, Y. (2000). Maintaining cultural stereotypes in the serial reproduction of narratives. *PSPB*, 26(5), 594–604.
Daley, D. J., & Kendall, D. G. (1965). Stochastic rumours. *J. Inst. Math. Appl.*, 1, 42–55.
Maki, D. P., & Thompson, M. (1973). *Mathematical Models and Applications*. Prentice-Hall.
Moreno, Y., Nekovee, M., & Pacheco, A. F. (2004). Dynamics of rumor spreading in complex networks. *PRE*, 69(6), 066130.
Sunstein, C. R. (2007). *Republic.com 2.0*. Princeton University Press.
Bakshy, E., Messing, S., & Adamic, L. A. (2015). Exposure to ideologically diverse news and opinion on Facebook. *Science*, 348(6239), 1130–1132.
Flaxman, S., Goel, S., & Rao, J. M. (2016). Filter bubbles, echo chambers, and online news consumption. *Public Opinion Quarterly*, 80(S1), 298–320.
Garrett, R. K. (2009). Echo chambers online? *JCMC*, 14(2), 265–285.
Guess, A., Nyhan, B., & Reifler, J. (2020). Exposure to untrustworthy websites in the 2016 U.S. election. *Nature Human Behaviour*, 4(5), 472–480.
Bail, C. A., et al. (2018). Exposure to opposing views on social media can increase political polarization. *PNAS*, 115(37), 9216–9221.
Del Vicario, M., et al. (2016). The spreading of misinformation online. *PNAS*, 113(3), 554–559.
Cinelli, M., et al. (2021). The echo chamber effect on social media. *PNAS*, 118(9), e2023301118.
Becker, J., Brackbill, D., & Centola, D. (2017). Network dynamics of social influence in the wisdom of crowds. *PNAS*, 114(26), E5070–E5076.
Becker, J., Porter, E., & Centola, D. (2019). The wisdom of partisan crowds. *PNAS*, 116(22), 10717–10722.
Mason, W., & Watts, D. J. (2012). Collaborative learning in networks. *PNAS*, 109(3), 764–769.
Lazer, D., & Friedman, A. (2007). The network structure of exploration and exploitation. *ASQ*, 52(4), 667–694.
Bond, R. M., et al. (2012). A 61-million-person experiment in social influence and political mobilization. *Nature*, 489(7415), 295–298.
Smaldino, P. E., & McElreath, R. (2016). The natural selection of bad science. *Royal Society Open Science*, 3(9), 160384.
Pennycook, G., et al. (2021). Shifting attention to accuracy can reduce misinformation online. *Nature*, 592(7855), 590–595.
Galesic, M., Olsson, H., & Rieskamp, J. (2012). Social sampling explains apparent biases in judgments of social environments. *Psychological Science*, 23(12), 1515–1523.

### 9.2 Inverse inference: source and structure

Shah, D., & Zaman, T. (2011). Rumors in a network: Who's the culprit? *IEEE Trans. Information Theory*, 57(8), 5163–5181.
Shah, D., & Zaman, T. (2012). Rumor centrality: A universal source detector. *ACM SIGMETRICS PER*, 40(1), 199–210.
Pinto, P. C., Thiran, P., & Vetterli, M. (2012). Locating the source of diffusion in large-scale networks. *PRL*, 109(6), 068702.
Zhu, K., & Ying, L. (2016). Information source detection in the SIR model. *IEEE/ACM Trans. Networking*, 24(1), 408–421.
Prakash, B. A., Vreeken, J., & Faloutsos, C. (2014). NetSleuth: efficiently spotting epidemic starting points. *KAIS*, 38(1), 35–65.
Lokhov, A. Y., Mézard, M., Ohta, H., & Zdeborová, L. (2014). Inferring the origin of an epidemic with a dynamic message-passing algorithm. *PRE*, 90(1), 012801.
Lokhov, A. Y., & Misiakiewicz, T. (2015). Efficient reconstruction of transmission probabilities in a spreading process from partial observations. arXiv:1509.06893.
Jiang, J., Wen, S., Yu, S., Xiang, Y., & Zhou, W. (2017). Identifying propagation sources in networks: state of the art. *IEEE Comms Surveys & Tutorials*, 19(1), 465–481.
Castro, R., Coates, M., Liang, G., Nowak, R., & Yu, B. (2004). Network tomography: recent developments. *Statistical Science*, 19(3), 499–517.
Gomez-Rodriguez, M., Leskovec, J., & Krause, A. (2010/12). Inferring networks of diffusion and influence. *KDD '10 / TKDD '12*.
Daneshmand, H., Gomez-Rodriguez, M., Song, L., & Schölkopf, B. (2014). Estimating diffusion network structures: Recovery conditions, sample complexity. *JMLR*.
Peixoto, T. P. (2019). Network reconstruction and community detection from dynamics. *PRL*, 123, 128301.
Peixoto, T. P. (2017). Bayesian stochastic blockmodeling. arXiv:1705.10225.
Newman, M. E. J., & Clauset, A. (2016). Structure and inference in annotated networks. *Nature Communications*, 7, 11863.
Mosteller, F., & Wallace, D. L. (1964). *Inference and Disputed Authorship: The Federalist*. Addison-Wesley.
Stamatatos, E. (2009). A survey of modern authorship attribution methods. *JASIST*, 60(3), 538–556.
Juola, P. (2008). Authorship attribution. *Foundations and Trends in IR*, 1(3), 233–334.
Koppel, M., Schler, J., & Argamon, S. (2009). Computational methods in authorship attribution. *JASIST*, 60(1), 9–26.
Koppel, M., Schler, J., & Bonchek-Dokow, E. (2007). Measuring differentiability: unmasking pseudonymous authors. *JMLR*, 8, 1261–1276.
Argamon, S., Koppel, M., Pennebaker, J. W., & Schler, J. (2009). Automatically profiling the author of an anonymous text. *CACM*, 52(2), 119–123.
Abbasi, A., & Chen, H. (2008). Writeprints: a stylometric approach. *ACM TOIS*, 26(2).
Brennan, M., Afroz, S., & Greenstadt, R. (2012). Adversarial stylometry. *ACM TISSEC*, 15(3).
Coulthard, M. (2004). Author identification, idiolect, and linguistic uniqueness. *Applied Linguistics*, 25(4), 431–447.
Coulthard, M., Johnson, A., & Wright, D. (2017). *An Introduction to Forensic Linguistics* (2nd ed.). Routledge.
Biber, D. (1995). *Dimensions of Register Variation*. CUP.
Nguyen, D., Doğruöz, A. S., Rosé, C. P., & de Jong, F. (2016). Computational sociolinguistics: a survey. *Computational Linguistics*, 42(3), 537–593.
Eckert, P. (2008). Variation and the indexical field. *Journal of Sociolinguistics*, 12(4), 453–476.
Bramsen, P., Escobar-Molano, M., Patel, A., & Alonso, R. (2011). Extracting social power relationships from natural language. *ACL '11*.
Diesner, J., & Carley, K. M. (2005). Revealing social structure from texts: meta-matrix text analysis. (CASOS / book chapter.)
Eagle, N., Pentland, A., & Lazer, D. (2009). Inferring friendship network structure by using mobile phone data. *PNAS*, 106(36), 15274–15278.
Linder, F., Desmarais, B. A., et al. (2020). Inferring social networks from unstructured text data. *Data & Policy*.
Brugere, I., Gallagher, B., & Berger-Wolf, T. (2018). Network structure inference: a survey. arXiv:1610.00782.

### 9.3 Dark and covert networks

Sparrow, M. K. (1991). The application of network analysis to criminal intelligence. *Social Networks*, 13(3), 251–274.
Krebs, V. (2002). Mapping networks of terrorist cells. *Connections*, 24(3), 43–52.
Baker, W. E., & Faulkner, R. R. (1993). The social organization of conspiracy. *American Sociological Review*, 58(6), 837–860.
Erickson, B. H. (1981). Secret societies and social structure. *Social Forces*, 60(1), 188–210.
Raab, J., & Milward, H. B. (2003). Dark networks as problems. *JPART*, 13(4), 413–439.
Everton, S. F. (2012). *Disrupting Dark Networks*. Cambridge University Press.
Cunningham, D., Everton, S. F., & Murphy, P. J. (2016). *Understanding Dark Networks*. Rowman & Littlefield.
Morselli, C. (2009). *Inside Criminal Networks*. Springer.
Carley, K. M. (2006). Destabilization of covert networks. *CMOT*, 12, 51–66.
Diesner, J., & Carley, K. M. (2005). Exploration of communication networks from the Enron email corpus. *CMOT*, 11(3).
Stohl, C., & Stohl, M. (2007). Networks of terror: theoretical assumptions and pragmatic consequences. *Communication Theory*, 17, 93–124.
Stohl, M., & Stohl, C. (2011). Secret agencies: the communicative constitution of a clandestine organization. *Organization Studies*, 32(9), 1197–1215.
Lindelauf, R., Borm, P., & Hamers, H. (2009). The influence of secrecy on the communication structure of covert networks. *Social Networks*, 31, 126–137.
Lindelauf, R., Hamers, H., & Husslage, B. (2013). Game-theoretic centrality analysis of terrorist networks. *EJOR*, 229(1).
Enders, W., & Su, X. (2007). Rational terrorists and optimal network structure. *JCR*, 51(1), 33–57.
Mastrobuoni, G., & Patacchini, E. (2012). Organized crime networks. *Review of Network Economics*, 11(3).
Calderoni, F. (2012). The structure of drug trafficking mafias: 'Ndrangheta and cocaine. *Crime, Law and Social Change*, 58, 321–349.
Bright, D. A., Hughes, C. E., & Chalmers, J. (2012). Illuminating dark networks. *Crime, Law and Social Change*, 57(2).
Natarajan, M. (2006). Understanding the structure of a drug trafficking organization. (Conversational analysis.)
Bakker, R. M., Raab, J., & Milward, H. B. (2012). A preliminary theory of dark network resilience. *JPAM*, 31(1), 33–62.
Duijn, P. A. C., Kashirin, V., & Sloot, P. M. A. (2014). The relative ineffectiveness of criminal network disruption. *Scientific Reports*, 4, 4238.
Crossley, N., Edwards, G., Harries, E., & Stevenson, R. (2012). Covert social movement networks and the secrecy–efficiency trade off: UK suffragettes. *Social Networks*, 34(4), 634–644.
Cavallaro, L., Ficara, A., De Meo, P., et al. (2020). Disrupting resilient criminal networks. *PLOS ONE*, 15(8).
Ficara, A., Cavallaro, L., Curreri, F., et al. (2022). Covert network construction, disruption, and resilience: a survey. *Mathematics*, 10(16), 2929.
Berlusconi, G., Calderoni, F., Parolini, N., et al. (2016). Link prediction in criminal networks. *PLOS ONE*, 11(4).
Burcher, M., & Whelan, C. (2018). Social network analysis as a tool for criminal intelligence. *Trends in Organized Crime*, 21, 278–294.
Carson, A. (2017). Covert communication: intelligibility and credibility of signaling in secret. (And related book/articles.)

### 9.4 Intelligence analysis, deception, credibility

Heuer, R. J. Jr. (1999). *Psychology of Intelligence Analysis*. CIA Center for the Study of Intelligence.
Heuer, R. J. Jr., & Pherson, R. H. (2019). *Structured Analytic Techniques for Intelligence Analysis* (3rd ed.). CQ Press / SAGE.
Pherson, K. H., & Pherson, R. H. (2020). *Critical Thinking for Strategic Intelligence* (3rd ed.). CQ Press.
Marrin, S. (2011). *Improving Intelligence Analysis*. Routledge.
Kent, S. (1964). Words of estimative probability. *Studies in Intelligence*, 8(4).
Friedman, J. A., & Zeckhauser, R. (2015). Handling and mishandling estimative probability. *Intelligence and National Security*, 30(1), 77–99.
Friedman, J. A., & Zeckhauser, R. (2012). Assessing uncertainty in intelligence. *Intelligence and National Security*, 27(6).
Mandel, D. R., & Barnes, A. (2014). Accuracy of forecasts in strategic intelligence. *PNAS*, 111(30), 10984–10989.
Mandel, D. R. (2015). Accuracy of intelligence forecasts from the consumer's perspective. *Policy Insights from BBS*, 2(1).
Mandel, D. R. (2021). Tracking accuracy of strategic intelligence forecasts. *Futures & Foresight Science*.
Tetlock, P. E. (2005). *Expert Political Judgment*. Princeton University Press.
Tetlock, P. E., & Gardner, D. (2015). *Superforecasting*. Crown.
Mellers, B., et al. (2014, 2015). Multiple papers on the Good Judgment Project. *Psychological Science*, *PNAS*, *JEP:G*.
Newman, M. L., Pennebaker, J. W., Berry, D. S., & Richards, J. M. (2003). Lying words: predicting deception from linguistic styles. *PSPB*, 29(5), 665–675.
Tausczik, Y. R., & Pennebaker, J. W. (2010). The psychological meaning of words: LIWC. *J. Language and Social Psychology*.
Hancock, J. T., Curry, L. E., Goorha, S., & Woodworth, M. (2008). On lying and being lied to: a linguistic analysis of deception in CMC. *Discourse Processes*, 45(1).
Vrij, A. (2008). *Detecting Lies and Deceit* (2nd ed.). Wiley.
Vrij, A., Granhag, P. A., & Mann, S. (2011). Outsmarting the liars: cognitive lie detection. *Current Directions*.
Bond, C. F., & DePaulo, B. M. (2006). Accuracy of deception judgments. *PSPR*, 10(3), 214–234.
DePaulo, B. M., et al. (2003). Cues to deception. *Psychological Bulletin*, 129(1), 74–118.
Johnson, M. K., & Raye, C. L. (1981). Reality monitoring. *Psychological Review*, 88(1), 67–85.
Steller, M., & Köhnken, G. (1989). Criteria-based statement analysis. (In Raskin, ed.)
Crawford, V. P., & Sobel, J. (1982). Strategic information transmission. *Econometrica*, 50(6), 1431–1451.
Kamenica, E., & Gentzkow, M. (2011). Bayesian persuasion. *AER*, 101(6), 2590–2615.
Bergemann, D., & Morris, S. (2019). Information design: a unified perspective. *JEL*, 57(1), 44–95.
Sobel, J. (2013). Giving and receiving advice. (Cambridge University Press chapter.)
Whaley, B. (1969/2007). *Stratagem: Deception and Surprise in War*. MIT/Artech House.
Bell, J. B., & Whaley, B. (1991). *Cheating and Deception*. Transaction.
Schum, D. A. (1994). *The Evidential Foundations of Probabilistic Reasoning*. Wiley.
Kadane, J. B., & Schum, D. A. (1996). *A Probabilistic Analysis of the Sacco and Vanzetti Evidence*. Wiley.
Tecuci, G., Schum, D. A., Marcu, D., & Boicu, M. (2016). *Intelligence Analysis as Discovery of Evidence, Hypotheses, and Arguments*. Cambridge University Press.

### 9.5 Disinformation and adversarial dynamics

Woolley, S. C., & Howard, P. N. (Eds.) (2018). *Computational Propaganda*. Oxford University Press.
Howard, P. N., Woolley, S. C., & Calo, R. (2018). Algorithms, bots, and political communication in the US 2016 election. *JITP*, 15(2), 81–93.
Bradshaw, S., & Howard, P. N. (2019). *The Global Disinformation Order*. Oxford Internet Institute.
Pacheco, D., et al. (2021). Uncovering coordinated networks on social media. *ICWSM*, 15, 455–466.
Sharma, K., Zhang, Y., Ferrara, E., & Liu, Y. (2021). Identifying coordinated accounts on social media. *KDD '21*.
Giglietto, F., Righetti, N., Rossi, L., & Marino, G. (2020). Coordinated link sharing behavior. *Information, Communication & Society*, 23(6), 867–891.
Ferrara, E., Varol, O., Davis, C., Menczer, F., & Flammini, A. (2016). The rise of social bots. *CACM*, 59(7), 96–104.
Davis, C. A., Varol, O., Ferrara, E., Flammini, A., & Menczer, F. (2016). BotOrNot. *WWW '16 Companion*.
Yang, K.-C., Varol, O., Hui, P.-M., & Menczer, F. (2020). Scalable and generalizable social bot detection. *AAAI '20*.
Yang, K.-C., Ferrara, E., & Menczer, F. (2022). Botometer 101. *J. Computational Social Science*, 5, 1511–1528.
Cresci, S., et al. (2017). The paradigm-shift of social spambots. *WWW '17 Companion*.
Cresci, S. (2020). A decade of social bot detection. *CACM*, 63(10), 72–83.
Cresci, S., et al. (2019). Better safe than sorry: an adversarial approach to improve social bot detection. *WebSci '19*.
Starbird, K., et al. (2014). Rumors, false flags, and digital vigilantes (Boston Marathon). *iConference '14*.
Starbird, K. (2017). Examining the alternative media ecosystem. *ICWSM '17*.
Starbird, K., Arif, A., & Wilson, T. (2019). Disinformation as collaborative work. *PACMHCI*, 3(CSCW), 1–26.
Starbird, K., DiResta, R., & DeButts, M. (2023). Influence and improvisation: participatory disinformation in 2020. *Social Media + Society*, 9(2).
Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. (Listed in 9.1; bridges to disinformation lit.)
Gallotti, R., Valle, F., Castaldo, N., Sacco, P., & De Domenico, M. (2020). Assessing the risks of "infodemics". *Nature Human Behaviour*, 4, 1285–1293.
Grinberg, N., Joseph, K., Friedland, L., Swire-Thompson, B., & Lazer, D. (2019). Fake news on Twitter during the 2016 election. *Science*, 363(6425), 374–378.
Bessi, A., & Ferrara, E. (2016). Social bots distort the 2016 US Presidential election. *First Monday*, 21(11).
Hindman, M., & Barash, V. (2018). *Disinformation, "Fake News" and Influence Campaigns on Twitter*. Knight Foundation.
Zügner, D., Akbarnejad, A., & Günnemann, S. (2018). Adversarial attacks on neural networks for graph data. *KDD '18*.
Bojchevski, A., & Günnemann, S. (2019). Adversarial attacks on node embeddings via meta learning. *ICLR '19*.
DiResta, R., et al. (2018). *The Tactics & Tropes of the Internet Research Agency*. New Knowledge / SSCI.
Linvill, D. L., & Warren, P. L. (2020). Troll factories: manufacturing specialized disinformation on Twitter. *Political Communication*, 37(4), 447–467.
Helmus, T. C., Bodine-Baron, E., et al. (2018). *Russian Social Media Influence*. RAND Corporation.
King, G., Pan, J., & Roberts, M. E. (2017). How the Chinese government fabricates social media posts. *APSR*, 111(3), 484–501.
Goldstein, J. A., et al. (2023). *Generative Language Models and Automated Influence Operations*. Stanford Internet Observatory / OpenAI / Georgetown CSET.
Ratkiewicz, J., et al. (2011). Detecting and tracking political abuse in social media. *ICWSM '11*.
Kumar, S., Cheng, J., Leskovec, J., & Subrahmanian, V. S. (2017). An army of me: sockpuppets in online discussion communities. *WWW '17*.

### 9.6 LLM-powered agent-based models

Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: interactive simulacra of human behavior. *UIST '23*. arXiv:2304.03442.
Park, J. S., et al. (2024). Generative agent simulations of 1,000 people. arXiv:2411.10109.
Park, J. S., et al. (2022). Social simulacra: creating populated prototypes for social computing systems. *UIST '22*. arXiv:2208.04024.
Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: using language models to simulate human samples. *Political Analysis*, 31(3), 337–351.
Aher, G., Arriaga, R. I., & Kalai, A. T. (2023). Using LLMs to simulate multiple humans. *ICML '23* / PMLR v202.
Horton, J. J., Filippas, A., & Manning, B. (2023). Large language models as simulated economic agents. NBER WP 31122.
Manning, B. S., Zhu, K., & Horton, J. J. (2024). Automated social science. NBER WP 32381.
Tornberg, P., Valeeva, D., Uitermark, J., & Bail, C. (2023). Simulating social media using LLMs. arXiv:2310.05984.
Chuang, Y.-S., Goyal, A., Harlalka, N., et al. (2024). Simulating opinion dynamics with networks of LLM-based agents. *Findings of NAACL '24*.
Gao, C., Lan, X., Lu, Z., Mao, J., Piao, J., Wang, H., Jin, D., & Li, Y. (2023). S³: social-network simulation system with LLM-empowered agents. arXiv:2307.14984.
Piao, J., et al. (2025). AgentSociety. arXiv:2502.08691.
Yang, Z., et al. (2024). OASIS: open agent social interaction simulations with one million agents. arXiv:2411.11581.
Tang, J., et al. (2024). GenSim. arXiv:2410.04360.
Vezhnevets, A. S., Agapiou, J. P., et al. (2023). Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia. arXiv:2312.03664.
Liu, X., Yan, Y., Chen, X., Liu, X., & Yang, L. (2024). LLM-driven multi-agent simulation for news diffusion under different network structures. arXiv:2410.13909.
Liu, T., Wang, J., et al. (2025). Simulating rumor spreading in social networks using LLM agents. arXiv:2502.01450.
Li, J., et al. (2024). FUSE / The stepwise deception. arXiv:2410.19064 (EMNLP '25).
Lu, X., et al. (2025). Decoding echo chambers: LLM-powered simulations. *COLING '25*.
Acerbi, A., & Stubbersfield, J. M. (2023). LLMs show human-like content biases in transmission chain experiments. *PNAS*, 120(44).
Boelaert, J., Coavoux, S., Ollion, É., Petev, I., & Präg, P. (2025). Machine bias: how do generative language models answer opinion polls? *Sociological Methods & Research*.
Cheng, M., Durmus, E., & Jurafsky, D. (2023). CoMPosT: characterizing and evaluating caricature in LLM simulations. *EMNLP '23*.
Cheng, M., Piccardi, T., & Yang, D. (2023). Marked personas. *ACL '23*.
Salecha, A., Ireland, M. E., Subrahmanian, V. S., et al. (2024). LLMs display human-like social desirability biases. *PNAS Nexus*, 3(12).
Wang, A., et al. (2023). The challenge of using LLMs to simulate human behavior: a causal inference perspective. arXiv:2312.15524.
De Marzo, G., Pietronero, L., et al. (2025). Emergent social conventions and collective bias in LLM populations. *Science Advances*, 11(20).
Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024). Synthetic replacements for human survey data? *Political Analysis*.
Larooij, M., & Tornberg, P. (2025). Validation is the central challenge for generative social simulation. *AI Review*.
Anthis, J., et al. (2025). LLM social simulations are a promising research method. arXiv:2504.02234.
Chopra, A., et al. (2024). On the limits of agency in agent-based models. arXiv:2409.10568.
Gao, C., Lan, X., Li, N., Yuan, Y., Ding, J., Zhou, Z., Xu, F., & Li, Y. (2024). LLM-empowered ABM and simulation: a survey. *Humanities and Social Sciences Communications*, 11.
Mou, X., et al. (2024). From individual to society: a survey on social simulation driven by LLM-based agents. arXiv:2412.03563.
Li, G., Hammoud, H., Itani, H., Khizbullin, D., & Ghanem, B. (2023). CAMEL. *NeurIPS '23*.
Wu, Q., Bansal, G., Zhang, J., et al. (2023). AutoGen. arXiv:2308.08155 / COLM '24.
Qiu, Y., et al. (2025). Understanding the information propagation effects of communication topologies in LLM-based multi-agent systems. arXiv:2505.23352 / EMNLP '25.

---

*End of review. Word count approximately 7,100 (excluding bibliography). Per-thread reports with abstracts and direct links available on request.*
