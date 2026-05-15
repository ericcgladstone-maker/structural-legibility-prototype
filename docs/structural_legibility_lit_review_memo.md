# Companion Memo: Structural Legibility Literature Review

*Compiled 2026-05-13. Companion to `structural_legibility_lit_review.md`.*

This memo records the differences between the prior review (`literature_review.md`, 2026-05-07) and the new review (`structural_legibility_lit_review.md`, 2026-05-13), the strongest and weakest sections of the new draft, citations that need verification, literatures still missing, a positioning map, a legacy-versus-LLM table, recommended next-pass search queries, and audience analysis.

---

## 1. Main differences between the old review and the new review

| Dimension | Old review (`literature_review.md`) | New review (`structural_legibility_lit_review.md`) |
|---|---|---|
| **Organizing question** | Can accuracy/fidelity/provenance be *estimated* from network-structural signals, and can such an estimator be *calibrated* in an LLM-ABM lab? | What traces of generative and transmissive history remain available for inference, and under what conditions can an LLM receiver use them to infer provenance, fidelity, and likely accuracy? |
| **Central construct** | Receiver-centered inference under varied information sets | Structural legibility of communication / communicative recoverability |
| **Definitional partition** | Accuracy, fidelity, provenance (three estimands) | Accuracy, fidelity, structural legibility (three referents, with legibility as a *property* of the message-process relation rather than a fourth estimand alongside accuracy and fidelity) |
| **Theoretical scaffolding** | Six literatures, identified as converging on a single gap | Three-layer architecture (legacy theory, computational bridge, LLM instantiation) with eight residue subtypes and eight propositions |
| **Treatment of LLMs** | Mutation engines for paper 1, with LLM receivers reserved for follow-up to avoid validity baggage | Mutation engines *and* receivers *and* evaluators *and* judges *and* inferred-provenance generators, all kept distinct as experimental positions |
| **Role of intelligence framing** | Primary applied domain, with disclaimers about generality | Secondary application, listed alongside organizational, scientific, journalistic, legal, and AI-mediated workflow contexts |
| **Relation to instrument** | Builds toward the receiver-inference matrix as the empirical core | Sketches an experimental design that produces a (structure × information regime × judgment target) matrix as theory-bearing data, not as a deployed instrument |
| **Coverage of psychology of communication** | Sparse (Heuer, Mandel, Tetlock, Bond and DePaulo, Vrij, Johnson and Raye) | Extensive (source-monitoring framework, reality-monitoring forensic tradition, epistemic vigilance, developmental selective trust, philosophical testimony) |
| **Coverage of linguistic residue** | Stylometry and computational sociolinguistics only | Evidentiality typology, epistemic stance, reported speech, pragmatics of evidential responsibility, plus the stylometry baseline |
| **Coverage of organizational communication** | Stohl and Stohl on clandestinity, Bramsen on superior-subordinate language | The above plus genre theory, CCO theory (Montreal School, Four Flows), resemiotization, audit-society |
| **Coverage of LLM-as-receiver** | Park, Argyle, Aher, Horton, Tornberg, Chuang, Liu, Acerbi, Boelaert, Bisbee | The above plus LLM-as-judge (Zheng, Liu G-Eval, Wang, Panickssery, Stureborg), calibration (Kadavath, Tian, Zhou), hallucination and attribution (Ji, Gao, Bohnet, Min), authorship (Huang, Uchendu), detection and watermarking (Mitchell, Sadasivan, Hans, Kirchenbauer), telephone game (Perez), model collapse (Shumailov, Alemohammad), multi-agent failure (Cemri) |
| **Use of propositions** | Six hypotheses tied to the staged paper plan | Eight propositions stated as theoretical claims with mechanism and empirical implication, plus seven research questions and eight hypotheses for the proposed experiment |
| **Bibliography size** | Roughly 180 entries | Roughly 220 entries with a separate "References to Verify" appendix |

The new review is also stylistically constrained per the writing brief. It avoids em dashes and avoids semicolons. The semicolon constraint produced a minor APA deviation (intra-parenthetical citation lists use commas rather than the conventional semicolons), which is flagged below under "decisions to revisit."

---

## 2. Strongest theoretical framing

The strongest move in the new review is the *triadic referent structure of a received message*: it is at once a partial representation of the world, a transformed descendant of a prior message, and an artifact of a communicative process. This partition immediately separates accuracy, fidelity, and structural legibility as properties of three different relations rather than as three competing estimands. The partition is also generative for residue theory in §4, because it grounds the claim that legibility is the property by which the receiver gains access to *the third relation* through the terminal artifact.

The second strongest move is the *detectability + discriminability* condition in §4.8. Many legibility claims in the literature fail because they implicitly assume detectability without discriminability, or vice versa. Specifying both conditions makes the propositions in §8 sharper and identifies an empirical bottleneck (residue that is detectable but non-discriminative) that the proposed design can measure directly.

The third strongest move is the *four-role distinction* for LLMs in §6.6: mutation engine, receiver, evaluator, judge, inferred-provenance generator. The LLM-ABM literature routinely conflates these roles, and the conflation generates fragile inference. The new review treats them as distinct experimental positions with separate measurement protocols.

---

## 3. Weakest or most underdeveloped sections

**§3 (Structure as a Condition of Transformation)** is weakest in the new draft. It rehearses the canonical network-epistemology findings but does not push the forward-versus-inverse-question framing as far as the rest of the review pushes its theoretical moves. The Bavelas-Leavitt reference is generic because no citation details for the present program's prior work were provided. A future revision should resolve those citations and should specify which exact mechanisms of structural conditioning (compression at hubs, drift in chains, reconciliation under cluster reinforcement) the residue theory in §4 is going to detect.

**§4.7 (Synthesis, Linear Relay, Clustered Reinforcement, Laundering)** is the most theoretically novel subsection but is the least grounded in cited literature. The configurational residue types (signs of synthesis, signs of linear relay degradation, signs of clustered reinforcement, signs of adversarial laundering) are largely the program's own construction and would benefit from a search pass for prior work in cross-corpus deduplication, near-duplicate detection, multi-document summarization residue, and adversarial paraphrase signatures. The conceptual framing is correct. The citation density needs to triple.

**§7.6 (LLM positioning)** is plausible but compressed. The argument that the proposed work is "a communication and network theory paper whose empirical laboratory uses LLMs" rather than "an LLM paper with background" is the central positioning move. It deserves a more explicit defense, including specific examples of how a reviewer trained in one tradition would read the paper if mispositioned.

**§9 (Empirical Design Sketch)** is intentionally a sketch rather than a full design. The discussion of identifiability tests preceding calibration claims is correct in principle but underspecified. A future revision should commit to a specific identifiability test family (mutual information bounds, distributional distinguishability under permutation, classifier-AUC ceilings).

**§5 (Receiver Inference)** integrates four large literatures (source monitoring, epistemic vigilance, intelligence, evidential Bayesian networks) into a single section, which forces a high abstraction level. Some readers may want more detailed treatment of either the cognitive-psychological or the institutional-Bayesian threads. Splitting into two subsections (cognitive-receiver, institutional-receiver) is a candidate revision.

---

## 4. Citations that need verification or supplementation

The new review includes a "References to Verify" appendix at the bottom of the main document, which lists the seven specific entries (Carson 2017, Clément 2010, Holt and Clift 2007, Murray 2014, NATO Admiralty Code, Shi et al. 2024, Uchendu et al. 2023, Zhang et al. 2023) where the search agents flagged uncertainty in venue, edition, or pagination. Each should be verified before formal submission.

Beyond those, the following entries are real but were retained from the prior review with limited re-verification in the present pass, and would benefit from a citation-correctness audit:

- All entries in §9.1 of the prior review related to opinion dynamics and learning models (DeGroot, Bala and Goyal, Friedkin and Johnsen, Hegselmann and Krause, Deffuant et al., Acemoglu et al.). The pagination and venue should be cross-checked.
- The Diesner and Carley CASOS entries are cited multiple times in the prior review with shifting publication details. A single canonical citation set should be settled on.
- The Carley (2006) "Destabilization of covert networks" entry needs volume and page numbers.
- Gomez-Rodriguez, Leskovec, and Krause (2010/2012) is cited as KDD 2010 in the prior review and as TKDD 2012 elsewhere. The new review uses KDD 2010 but the user should pick one canonical reference per citation.
- Carson (2017) is cited generically. The new review's reference list provisionally uses Carson's *International Organization* article, but the book-length treatment (*Secret Wars*, 2018) may be the better citation depending on use.

**Decisions to revisit:**

- *Semicolon avoidance versus APA conformance.* The user brief prohibited semicolons. APA convention uses semicolons to separate multi-reference parenthetical citations. The new review resolves this by using commas inside parenthetical citation lists, which is a minor deviation from APA. If strict APA is required at submission, this should be revisited. If the avoidance was intended only for prose semicolons, a one-line global edit reverts the change.
- *Use of "et al." for citations with three or more authors.* APA 7th edition prescribes et al. from the first citation for three or more authors. The new review uses full author lists on some first citations for clarity and et al. on others. A consistent rule should be applied.
- *Inline citation density.* The new review uses dense parenthetical citation, which is appropriate for a literature review but heavy for a theoretical paper. A future revision targeting a communication-theory venue may want to thin the citations and emphasize the propositions.

---

## 5. Missing literatures that likely need a future search pass

The present pass searched four major adjacent literatures (psychology of source and credibility, linguistics of stance and evidentiality, organizational and rumor communication, LLM-as-receiver). The following bodies of work were either touched lightly or not covered and would benefit from a future search pass.

1. **Provenance reasoning in archives, journalism, and information science.** The new review treats provenance as an inferential target but does not draw on the archival, journalistic-sourcing, or library-and-information-science literatures on provenance reasoning. Likely sources: archival theory (Yeo on records), journalism studies on source verification (Bell, Tuchman, Reich), W3C PROV ontology for provenance metadata, and the digital-humanities tradition on textual transmission and stemmatology.

2. **Genre theory and bureaucratic compression at greater depth.** The new review draws on Bakhtin, Swales, Bazerman, Yates and Orlikowski, Iedema, and Smith. A deeper pass should include North American New Rhetoric (Devitt, Miller on genre as social action), genre ecologies (Spinuzzi), and discourse analysis of bureaucratic forms (Smith on texts, but also further institutional ethnography work).

3. **Forensic linguistics beyond stylometry.** The Coulthard tradition is cited from the prior review, but forensic-linguistic work on authorship attribution under adversarial conditions, speaker profiling, and discourse analysis of disputed texts deserves a dedicated pass. The Aston University forensic-linguistics group and the Hofstra/INTELL-fora line are likely starting points.

4. **LLM-as-judge calibration at greater depth.** The present pass identified the load-bearing LLM-as-judge papers but did not exhaustively cover calibration of LLM judgments under heterogeneous prompts and rubrics. The recent 2025 literature on judge consistency, judge robustness, and meta-evaluation is large and moving quickly.

5. **Source localization and stylometric joint inference.** The prior review identifies a triangular gap between source-localization-on-graphs, network-inference-from-cascades, and stylometry. The new review preserves this framing but the gap-filling literature in 2024-2026 (joint timing-content inference, content-aware diffusion source-detection) should be re-searched.

6. **Information design and strategic communication for non-economists.** Crawford-Sobel, Kamenica-Gentzkow, and Bergemann-Morris are cited from the prior review. The downstream computational-economics literature on adversarial information design and the political-communication translation of these models is missing.

7. **Children's selective trust at greater depth.** Koenig-Harris, Harris-Corriveau, and Clément are cited, but the broader developmental literature on children's source-monitoring and trust calibration (Lane, Wandell, Heyman, Sodian) should be searched if the developmental analog is to be argued more explicitly.

8. **Anthropology of communication and oral tradition.** Communication-as-transformation and serial reproduction are well-grounded in psychology and sociology, but the anthropology of oral tradition (Vansina, Goody, Finnegan, Bauman) provides a cultural-transmission baseline that the new review does not draw on.

9. **Conversational repair, common ground, and grounding.** Clark's work on common ground (Clark and Brennan, Clark on uses of language) is cited only via Clark and Gerrig on quotation. A separate pass on grounding and repair (Schegloff, Clark and Brennan, Garfinkel) would strengthen the receiver-inference theory in §5.

10. **Disinformation laundering and cross-platform provenance loss.** The prior review covers participatory disinformation (Starbird) and cross-platform laundering (Yang et al., Starbird DiResta). The new review preserves the relevant claims but the empirical literature on provenance loss across platform boundaries is growing and should be re-searched.

---

## 6. Positioning map

The new review identifies six adjacent literatures, what each explains, what each misses, and where the proposed contribution sits relative to each.

| Adjacent literature | What it explains | What it does not address | Where this project contributes |
|---|---|---|---|
| **Communication theory and CCO** | Message transformation, genre, stance, production format, the constitutive role of communication in institutions | Computationally testable predictions about how structural variation maps to recoverable residue in terminal messages, LLMs as receivers or transmission media | Provides the missing empirical bridge while drawing on the conceptual vocabulary (animator/author/principal, ventriloquism, resemiotization) |
| **Network science and network epistemology** | Diffusion, collective inference, topology, redundancy, clustering, centralization, conditions for convergence on truth | Semantic residues that topology leaves in terminal messages, receiver inference over hidden histories | Content-coupled extension of the inverse-inference problem, residue in terminal content rather than only timing as the inferential signal |
| **Serial reproduction, rumor, cultural transmission** | Mutation under transmission, leveling, sharpening, assimilation, gist preservation, schema-consistent distortion, emotional salience | Non-linear network structures, receiver-inference question, LLMs as transmitters and receivers | Generalizes serial-reproduction designs to networked transmission with continuous-text content and adds the receiver-inference framing |
| **Computational sociolinguistics, stylometry, forensic linguistics** | Social, authorial, and role traces in language, with high accuracies for demographic and authorship inference | Propagation structure, transmission history from textual residue, inference at the level of a chain rather than a single producer | Propagation-aware extension of stylometric and sociolinguistic inference, with the target shifted from authorship to the structural process producing the terminal form |
| **Intelligence analysis and social epistemology** | Credibility, testimony, evidence aggregation, source reliability, calibration, institutional management of uncertainty | Computational measurement of structural residue, LLMs as receivers, experimental manipulation of receivers | Setting in which the constructs of credibility assessment become empirically tractable under known ground truth, with the receiver itself as a manipulable variable |
| **LLM and AI-mediated communication** | LLM judgment behavior, simulation fidelity, hallucination, calibration, source attribution, summarization, synthetic-social-system dynamics | Structural legibility as a *theory of communication*, LLMs as instruments rather than as the object of study | Theoretical reframe and experimental design that uses LLMs as the empirical laboratory for a communication-theoretic question |

The unoccupied intersection is the conjunction of: (a) structure-conditioned message transformation, (b) recoverable residue or structural legibility, (c) receiver inference over hidden communicative histories, and (d) LLM-based computational instantiation with both mutation channel and receiver as experimentally manipulable. No existing program combines the four. Each component has neighbors.

---

## 7. Legacy theory versus LLM-specific literatures

| Theme | Legacy non-LLM literature (theoretical substrate) | LLM-specific literature (empirical instantiation) |
|---|---|---|
| **Communication as transformation** | Bartlett 1932, Allport and Postman 1947, Mesoudi and Whiten 2008, Kashima 2000, Knapp 1944, Shibutani 1966, Buckner 1965, Rosnow 1988, 1991, DiFonzo and Bordia 2007 | Acerbi and Stubbersfield 2023 (single LLM serial reproduction), Perez et al. 2024 (telephone game), Brinkmann et al. 2023 (machine culture) |
| **Structure as condition of transformation** | Bavelas 1950, Leavitt 1951, Centola 2010, Watts 2002, Centola and Macy 2007, Zollman 2007, Lazer and Friedman 2007, Golub and Jackson 2010, Becker and Centola 2017, Mason and Watts 2012, Lindelauf et al. 2009, Stohl and Stohl 2007, 2011 | Liu et al. 2024 (news diffusion), Chuang et al. 2024 (opinion dynamics), Qiu et al. 2025 (topology and information propagation), Liu et al. 2025 (rumor spreading) |
| **Residue, evidentiality, stance** | Aikhenvald 2004, Chafe and Nichols 1986, Willett 1988, Faller 2002, Squartini 2001, Mushin 2001, Biber and Finegan 1989, Hyland 1998, Du Bois 2007, Lakoff 1973, Vološinov 1929, Bakhtin 1981, 1986, Goffman 1981, Clark and Gerrig 1990, Vandelanotte 2009, Tannen 1989, Grice 1975, Brandom 1994, MacFarlane 2011, Williamson 2000, Sperber and Wilson 1995, Recanati 2000, Murray 2014 | BioScope (Vincze et al. 2008), CoNLL-2010 (Farkas et al. 2010), committed-belief (Diab et al. 2009, Prabhakaran et al. 2010), stance detection (Mohammad et al. 2016, Augenstein et al. 2016, Zubiaga et al. 2018), LLM-judge stance reading (implicit across the LLM-as-judge corpus) |
| **Genre, institutional discourse, CCO** | Bakhtin 1986, Swales 1990, Bazerman 1988, Yates and Orlikowski 1992, 2002, Berkenkotter and Huckin 1995, Fairclough 1992, Iedema 2001, 2003, Power 1997, Star and Strauss 1999, Smith 2001, Taylor and Van Every 2000, Cooren 2004, 2010, McPhee and Zaug 2000, Ashcraft et al. 2009, Schoeneborn et al. 2014, Putnam and Nicotera 2009 | No major LLM-specific work yet on bureaucratic-style transformation chains or genre-conditioned LLM transmission. Cemri et al. 2025 on multi-agent LLM failure is the closest. |
| **Source monitoring and reality monitoring** | Johnson and Raye 1981, Johnson Hashtroudi and Lindsay 1993, Mitchell and Johnson 2000, 2009, Johnson 2006, Sporer 1997, 2004, 2016, Masip et al. 2005, Vrij 2008, 2015 | Reality-monitoring style residue features are implicit in LLM-as-judge fact-checking and in detail-counting summarization evaluation, but no LLM-specific framing under the source-monitoring label has emerged. |
| **Epistemic vigilance, testimony, credibility** | Sperber et al. 2010, Mascaro and Sperber 2009, Mercier 2020, Mercier and Sperber 2017, Coady 1992, Burge 1993, Hardwig 1985, Fricker 1994, Lackey 2008, Goldberg 2007, Koenig and Harris 2005, Harris and Corriveau 2011, Clément 2010, Loftus and Palmer 1974, Wells and Olson 2003, Wells Memon and Penrod 2006 | Sycophancy work (Sharma et al. 2024, Perez et al. 2023), persuasion (Salvi et al. 2025), LLM-as-judge biases (Wang et al. 2024, Panickssery et al. 2024, Stureborg et al. 2024). The LLM tradition has not engaged the philosophical-testimony or developmental-trust literatures. |
| **Intelligence analysis and Bayesian evidence aggregation** | Heuer 1999, Heuer and Pherson 2019, Kent 1964, Friedman and Zeckhauser 2012, 2015, Mandel 2015, 2021, Mandel and Barnes 2014, Tetlock and Gardner 2015, Mellers et al. 2014, 2015, Bond and DePaulo 2006, DePaulo et al. 2003, Vrij 2008, Newman et al. 2003, Tausczik and Pennebaker 2010, Hancock et al. 2008, Schum 1994, Kadane and Schum 1996, Tecuci et al. 2016, Crawford and Sobel 1982, Kamenica and Gentzkow 2011, Bergemann and Morris 2019 | Quelle and Bovet 2024 and Hoes et al. 2023 on LLM fact-checking are the closest. No mature LLM literature on Bayesian evidence aggregation or ACH-style structured analysis. |
| **LLMs as transmission and as receivers** | (no legacy LLM tradition by definition) | Park et al. 2022, 2023, 2024, Argyle et al. 2023, Aher et al. 2023, Horton et al. 2023, Tornberg et al. 2023, Manning et al. 2024, Acerbi and Stubbersfield 2023, Boelaert et al. 2025, Cheng et al. 2023a, 2023b, Bisbee et al. 2024, Salecha et al. 2024, Larooij and Tornberg 2025, Zheng et al. 2023, Liu et al. 2023, Wang et al. 2024, Panickssery et al. 2024, Stureborg et al. 2024, Bai et al. 2022, Quelle and Bovet 2024, Hoes et al. 2023, Kadavath et al. 2022, Lin et al. 2022, Zhou et al. 2023, Tian et al. 2023, Ji et al. 2023, Zhang et al. 2023, Gao et al. 2023a, 2023b, Bohnet et al. 2022, Min et al. 2023, Huang et al. 2024a, 2024b, Uchendu et al. 2023, Mitchell et al. 2023, Sadasivan et al. 2023, Hans et al. 2024, Kirchenbauer et al. 2023, Shi et al. 2024, Shumailov et al. 2024, Alemohammad et al. 2024, Perez et al. 2024, Brinkmann et al. 2023, Cemri et al. 2025 |

The table makes a point that is implicit but not stated outright in the main review. The legacy-theory column is much longer than the LLM-specific column. This is the correct ratio for a *communication and network theory paper* whose empirical laboratory uses LLMs. It is the wrong ratio for an LLM paper.

---

## 8. Recommended search queries for the next literature pass

The following queries, run as a parallel batch, should fill the residual gaps identified in §5.

**Provenance reasoning and stemmatology.**
- "provenance reasoning archival theory records continuum"
- "W3C PROV ontology" and "computational provenance"
- "stemmatology textual transmission digital humanities"
- "journalism source verification credibility cues"

**Genre theory and institutional discourse, deeper pass.**
- "New Rhetoric genre social action Miller Devitt"
- "genre ecologies Spinuzzi"
- "institutional ethnography Smith texts"
- "discourse analysis bureaucratic forms"

**Forensic linguistics beyond stylometry.**
- "forensic linguistics authorship adversarial conditions"
- "speaker profiling forensic linguistics"
- "Aston forensic linguistics" or "Coulthard tradition" newer work

**LLM-as-judge calibration depth pass.**
- "LLM judge calibration 2025"
- "LLM evaluator robustness rubric variation"
- "meta-evaluation LLM judges"
- "judge LLM cross-model agreement"

**Source localization with content channel.**
- "joint topology content inference cascade"
- "content-aware diffusion source detection"
- "stylometric source localization network"

**Information design and political communication.**
- "Bayesian persuasion political communication"
- "information design strategic communication empirical"
- "adversarial information design computational"

**Children's selective trust, deeper pass.**
- "selective trust development informant accuracy"
- "children source monitoring development"
- "developmental epistemic vigilance"

**Oral tradition and cultural transmission anthropology.**
- "oral tradition Vansina Goody anthropology"
- "cultural transmission ethnography variation"
- "Bauman performance verbal art"

**Common ground and grounding.**
- "common ground Clark grounding repair"
- "conversational repair Schegloff"
- "joint action linguistic coordination"

**Cross-platform disinformation laundering, recent.**
- "cross-platform disinformation laundering 2024 2025"
- "provenance loss social media platform"
- "narrative migration across platforms computational"

**Configurational residue and adversarial paraphrase.**
- "near duplicate detection multi-document"
- "adversarial paraphrase stylistic laundering"
- "multi-document summarization residue"

**Residue evaluation in LLM summarization.**
- "summarization information loss residue"
- "LLM summarization faithfulness compression"

---

## 9. Likely primary audience and two alternatives

**Primary audience: computational social science.**

The proposed paper is best positioned for venues that admit theoretical contributions framed around new constructs and have methodological tooling to engage the experimental design. Specific candidates include the *Journal of Computational Social Science*, *Nature Human Behaviour* for the more empirically substantial follow-up papers, *PNAS Nexus*, *EPJ Data Science*, and the proceedings of conferences such as ICWSM and ASONAM. The advantages of this positioning are that it maximizes integrative reach (the paper speaks to network science, communication, and AI together), it admits both theoretical and experimental contributions, and it has reviewer pools familiar with the LLM-ABM literature. The risks are twofold. The paper must defend itself against narrow communication-theoretic critiques (that the residue analytics are under-specified) and against narrow AI-evaluation critiques (that the LLM design is not novel enough as engineering). The recommended hedge is to lead with the theoretical reframe in §§1-4, place the experimental design in §§9-10, and treat §6 (LLMs as receivers and so on) as a *theoretical position* on a class of receivers rather than as a new engineering contribution.

**Alternative audience one: communication theory and organizational communication.**

Venues such as *Communication Theory*, *Management Communication Quarterly*, *Organization Studies*, *Journal of Communication*, and *Human Communication Research* are well-positioned for the residue and CCO-adjacent material in §§3-5. The advantages are theoretical depth, reviewer engagement with the CCO and genre traditions, and a natural home for the §4 residue theory. The risks are that the LLM instantiation in §6 will be read either as an engineering distraction or as out-of-paradigm, and that the experimental design in §9 will be undervalued. The recommended adaptation is to deepen the CCO and genre material, narrow the LLM treatment to its theoretical relevance for the receiver question, and treat the experiment as motivated by a long communication-theoretic tradition rather than as a methodological innovation.

**Alternative audience two: AI and society / NLP venues with workshop tracks on LLM evaluation.**

Venues such as the NLP/AI-and-Society workshops at ACL, EMNLP, NAACL, and NeurIPS, the *AI Magazine* community, *AI & Society*, and the *Journal of Artificial Intelligence Research* would host the §6 material directly. The advantages are direct reviewer engagement with the LLM-as-judge and LLM-as-receiver constructs, faster turnaround, and natural alignment with the §9 experimental sketch. The risks are that the legacy-theory material in §§2-5 will be read as background rather than as load-bearing, that the structural-legibility construct will be assimilated to existing LLM-evaluation vocabulary, and that the paper will read as an LLM paper with background, the framing the present review explicitly resists. The recommended adaptation is to retain the full legacy-theory architecture and to frame the LLM component explicitly as a *test bed for a communication-theoretic claim*.

The strongest single recommendation is the computational-social-science primary positioning with retained option to retarget to communication-theory venues if reviewer feedback in CSS treats the residue theory as out-of-scope.

---

*End of memo.*
