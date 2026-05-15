# Structural Legibility of Communication: Inferring Provenance, Fidelity, and Accuracy from Messages and Their Histories

*Working document. Compiled 2026-05-13. Supersedes the earlier instrument-facing review (`literature_review.md`, 2026-05-07).*

---

## 1. Introduction: From Accuracy Estimation to Communicative Recoverability

A prior version of this review (compiled 2026-05-07) asked an instrument-facing question. It asked whether the accuracy of an intercepted communication could be estimated from network-structural signals, and whether such an estimator could be calibrated in a controlled laboratory of LLM-powered agents. That question is real and has applied value. It is also the wrong starting point for a theoretical paper, because it commits in advance to a particular kind of artifact (an estimator), a particular kind of receiver (an operator with a dashboard), and a particular kind of contribution (calibration of a measurement device). A more general theoretical question lies beneath it.

The revised question is this: when a message reaches a receiver, what traces of its generative and transmissive history remain available for inference, and under what conditions can a receiver, including an LLM receiver, use those traces to infer structural provenance, fidelity, and likely accuracy. The central theoretical construct is the *structural legibility* of communication, by which we mean the degree to which a received message preserves recoverable evidence of the communication structure, role configuration, path, and transmission process that produced it. The broader inferential problem, of which legibility is one component, is *communicative recoverability*: the problem of inferring hidden production and transmission conditions from the communicative artifact and whatever partial history is available alongside it.

This shift in framing is more than rhetorical. It moves the analytic object from a fixed quantity that a receiver wants to estimate (the message's accuracy) to a variable property of the communicative situation (the legibility of its production history in its terminal form). It allows the review to engage with literatures that the instrument-facing framing held at arm's length, including evidentiality in typological linguistics, the source-monitoring framework in cognitive psychology, epistemic vigilance in social-evolutionary psychology, the communicative constitution of organizations, rumor morphology, and recent work on LLMs as evaluators and as relays. It also reorders the empirical implications. The applied logic that motivated the earlier review (terminal communication then inferred structural conditions then narrowed provenance hypotheses then better priors over source, incentive, competence, access, and distortion risk then better-calibrated judgments of fidelity and accuracy) becomes a downstream consequence of the theory rather than its organizing question.

A few definitions, used throughout, must be kept distinct.

**Accuracy** denotes correspondence between the message and the state of the world it describes. Accuracy is a property of the message-world relation.

**Fidelity** denotes correspondence between the received message and an earlier or original message in the chain that produced it. Fidelity is a property of the message-message relation. A high-fidelity transmission can carry an inaccurate message faithfully. A low-fidelity transmission can produce an accurate message by accident.

**Structural legibility** denotes the degree to which a received message preserves recoverable evidence of the communication structure, path, role configuration, or transmission process that produced it. Legibility is a property of the message-process relation. It is mediated by the residues that transformation leaves in the artifact and by the discriminative power of those residues across alternative production histories.

**Communicative recoverability** denotes the broader inference problem in which a receiver, given the terminal message plus any partial history, attempts to reconstruct hidden production and transmission conditions. Recoverability subsumes legibility but also includes the receiver's prior knowledge of plausible source types, incentives, networks, and competences. The theoretical claim of this review is that accuracy and fidelity judgments are not read directly off content, but are produced by inference over partially observable communicative processes, and that the quality of those judgments depends on the legibility of the relevant residues.

A received message has at least three referents, and confusion among them recurs across literatures. It is, first, a partial representation of the *world* it claims to describe. It is, second, a transformed descendant of a *prior message* or source observation. It is, third, an artifact of a *communicative process* that traversed some structure of roles, relays, syntheses, omissions, and amplifications. Accuracy concerns the first relation. Fidelity concerns the second. Structural legibility concerns the third. The central claim of the present program is that the third relation is theoretically prior to the first two for the purposes of receiver inference, because the receiver does not have direct access to either the world or the prior message, only to the terminal artifact and to whatever partial history accompanies it.

The remainder of the review proceeds as follows. Section 2 reviews the literatures that establish communication as transformation rather than transport. Section 3 reviews work that treats network structure as a condition of transformation. Section 4 develops a theory of residue, drawing on stylometry, evidentiality, reported speech, genre theory, rumor morphology, and forensic linguistics. Section 5 reviews receiver-side inference over hidden communicative histories, drawing on source monitoring, reality monitoring, epistemic vigilance, philosophical testimony, intelligence analysis, and Bayesian evidence aggregation. Section 6 turns to LLMs as receivers, relays, and evaluators, drawing on recent work in LLM-as-judge, LLM calibration, hallucination, source attribution, authorship attribution at scale, multi-agent drift, and model collapse. Section 7 locates the contribution by identifying the closest literatures and specifying where the proposed work sits relative to each. Section 8 synthesizes the review into eight propositions. Section 9 sketches the empirical implications for an LLM-based computational experiment. Section 10 states research questions and hypotheses. Section 11 concludes.

---

## 2. Communication as Transformation

The premise of the review is that transmission changes messages. This is well established empirically but is treated unevenly across the literatures that bear on the present question.

The foundational empirical work is Bartlett (1932), whose serial reproduction studies showed that successive retellings of a story produce systematic distortions, with detail loss, normalization toward the receiver's cultural schemas, and rationalization of unfamiliar elements. Allport and Postman (1947) refined this into three processes that became canonical in rumor research, *leveling* (radical compression and loss of detail), *sharpening* (selective amplification of a few salient features), and *assimilation* (warping of remaining content toward the listener's pre-existing schemas, stereotypes, and motives). Kashima (2000) demonstrated that the stereotype-consistent component of a transmitted narrative is preferentially preserved across chains, while stereotype-inconsistent material is leveled or refigured. Mesoudi and Whiten (2008) consolidated the cultural-transmission tradition, showing that transmission chains both reveal universal content biases (toward gist, emotion, social information, minimally counterintuitive concepts) and serve as a methodological tool for studying cumulative culture.

The wartime and post-war rumor literature provides the most empirically developed account in social science of which features survive transmission. Knapp (1944) classified wartime rumors into pipe-dream, bogie, and wedge-driving forms, each with characteristic morphologies. Caplow (1947) showed in a basic-training camp that rumor accuracy and form depended on the social-interest geometry of the rumor public rather than on properties of individual transmitters. Shibutani (1966) reframed rumor as *improvised news*, a collective problem-solving response activated when institutional information supply fails relative to demand, and Buckner (1965) showed that the direction of mutation depends on the structural configuration of the transmitting network. Rosnow (1988, 1991) and DiFonzo and Bordia (2007a, 2007b) formalized rumor accuracy and form as an interaction of anxiety, ambiguity, credulity, importance, and network embeddedness. The rumor tradition is theoretically generative for the present project because it treats mutation as law-governed rather than as noise.

Computational replication of these findings using LLMs is now possible and has begun. Acerbi and Stubbersfield (2023) showed that a single LLM operating as a serial-reproduction transmitter exhibits the same content biases as human transmission chains, with preferential survival of stereotype-consistent, emotional, and minimally counterintuitive material. Perez et al. (2024) extended this to *iterated cultural transmission* in which an LLM passes a message to itself or to other LLMs across many hops, documenting cumulative drift toward attractor states (lower toxicity, certain length regimes, certain stylistic templates), with attractor strength varying by content property and by prompt openness. Brinkmann et al. (2023) framed the broader phenomenon as *machine culture*, the population-scale dynamics that emerge when LLMs participate as agents in cultural transmission. These results constitute a positive existence proof that LLM-mediated transmission preserves some of the systematicity observed in human transmission while introducing additional biases of its own.

A different cluster of literatures treats the propagated item as essentially stable. Diffusion models from Daley and Kendall (1965) and Moreno, Nekovee, and Pacheco (2004) onward typically represent the spreading item as an opaque token. Cascade-shape analyses (Vosoughi, Roy, & Aral, 2018, Goel, Anderson, Hofman, & Watts, 2016) measure depth, breadth, structural virality, and speed but typically hold message identity fixed across the cascade. Network-inference-from-cascade-timing (Gomez-Rodriguez, Leskovec, & Krause, 2010, Lokhov & Misiakiewicz, 2015, Peixoto, 2019) treats arrival times as the signal and abstracts away from textual content. The result is a literature that is technically rich on the structural side and treats content mutation as outside its analytic frame.

Institutional and bureaucratic communication adds a further mode of transformation that the diffusion and serial-reproduction literatures do not foreground. Iedema (2001, 2003) develops the concept of *resemiotization*, the process by which content is repeatedly recoded into more abstract, more durable, and more institutionally legible forms as it moves through organizational hierarchies (talk to minutes to memos to policy). Star and Strauss (1999) and Power (1997) show that what is systematically erased in such recodings is local indexicality, articulation work, and the negotiation that produced the document. Genre theory (Bakhtin, 1986, Swales, 1990, Bazerman, 1988, Yates & Orlikowski, 1992, 2002, Berkenkotter & Huckin, 1995, Fairclough, 1992) treats genres as socio-cognitive templates that compress recurrent communicative problems into reusable forms and stabilize institutional power across encounters. Smith (2001) argues that text-mediated coordination is the means by which the trans-local organizational form exists at all, making textual artifacts the privileged residue site for institutional analysis. Together these literatures establish that communication is transformed not only by individual cognitive processes during retelling but by the structural-institutional setting in which it is produced and relayed.

The central claim of this section is that communication is not a neutral transport mechanism. Transmission systematically changes propositional content, evidentiary grounding, specificity, confidence, causal structure, pragmatic force, genre, and stance. The relevant question for the present program is not whether transformation occurs (it does), but which transformations leave recoverable evidence in the terminal artifact, and which dissolve into the noise floor.

---

## 3. Structure as a Condition of Transformation

If transmission transforms messages, then the structure of transmission should shape the transformation. This claim has been examined under several headings.

The classical small-group communication-network experiments are the locus classicus. Bavelas (1950) and Leavitt (1951) compared centralized topologies (wheel, chain) with decentralized ones (circle, all-channel) on simple coordination tasks, and found that centralized structures resolved simple coordination problems faster but were less reliable on ambiguous tasks and produced lower morale at peripheral positions. The present program's prior Bavelas-style and information-mutation studies, conducted with LLM agents, extend this tradition into continuous-text message conditions where mutation is itself the object of measurement. (Detailed citations for the present program's prior work are deferred to the program's internal documentation rather than included here as formal references.)

The contemporary network-science and network-epistemology literature has accumulated several robust findings. Centola (2010), Watts (2002), and Centola and Macy (2007) show that topology shapes diffusion holding individual behavior fixed, with simple and complex contagions behaving oppositely with respect to long ties. Vosoughi, Roy, and Aral (2018) document at scale that falsehoods diffuse farther, faster, deeper, and more broadly than truths, with topology-specific signatures. Zollman (2007, 2013) and Lazer and Friedman (2007) establish that less-connected epistemic networks sometimes converge on truth more reliably than more-connected ones, because moderate isolation preserves heterogeneity of trial. Golub and Jackson (2010) characterize the conditions under which DeGroot-style social learning converges on the truth, and identify the "prominent group" obstruction to wisdom-of-crowds outcomes. Becker, Brackbill, and Centola (2017) and Becker, Porter, and Centola (2019) show that decentralized (egalitarian) influence improves numerical-estimation accuracy in experimental conditions. Mason and Watts (2012) qualify the picture by showing that efficient networks help on parameter-search problems. The reconciliation across these findings is task-dependent and remains theoretically open.

The dark-networks literature contributes a different angle. Sparrow (1991), Baker and Faulkner (1993), Krebs (2002), and Lindelauf, Borm, and Hamers (2009) establish that covert networks face a *secrecy-efficiency tradeoff* that pushes optimal topologies away from small-world structures and toward stars or paths under joint penalties for detection risk and information-utility loss. Stohl and Stohl (2007, 2011) develop the *communicative constitution of clandestinity*, the claim that secrecy is not the absence of signal but a structured signaling regime in which messages are designed to be intelligible to insiders while flagging resolve or affiliation to outsiders. Carson (2017) extends this to covert signaling in international relations. The stylized communication facts that emerge are central to a theory of residue: dark-network messages tend to be shorter and less elaborated, euphemistic or pre-coded with substituted referents, redundant in safety-critical respects but sparse in routine information, asymmetric in role-use of language, and bursty rather than continuous. These are systematic properties of communicative form under a particular structural-strategic regime.

Communicative-constitution-of-organizations (CCO) theory adds a further reframe. Taylor and Van Every (2000), Cooren (2004, 2010), McPhee and Zaug (2000), Ashcraft, Kuhn, and Cooren (2009), and Schoeneborn et al. (2014) treat organizations not as containers in which communication occurs but as precipitates of communicative activity. On the Montreal School view, texts have genuine agency, contracts, memos, and signs speak when their authors are absent and carry the voices of distant authorities, an effect Cooren calls *ventriloquism*. McPhee's Four Flows model distinguishes membership negotiation, self-structuring, activity coordination, and institutional positioning as constitutive message-types. The implication for the present project is that structural residue in a message is not only archaeology of a prior structure but a *constitutive act* that produces and modifies the structure it represents. This complicates inverse inference, because the structure to be inferred is partly performed by the very messages from which the inference is made.

The forward and inverse readings of these literatures give a sharp pair of questions.

The forward question is: do some structures produce more accurate or higher-fidelity messages than others, and under what task and content conditions does the ordering hold?

The inverse question is: do some structures produce messages whose origins are more legible to a receiver than messages from other structures, and which structural features are most discriminable from terminal artifacts?

The forward question has been studied extensively (Zollman, Lazer-Friedman, Golub-Jackson, Becker-Centola, Mason-Watts), with a task- and content-dependent answer. The inverse question, in the receiver-inference form posed here, is not directly addressed in the network-epistemology tradition. Network-inference-from-cascade-timing (Gomez-Rodriguez et al., 2010, Lokhov et al., 2014, Peixoto, 2019) treats the inverse problem on timing data alone. Stylometry and authorship attribution (Stamatatos, 2009, Argamon, Koppel, Pennebaker, & Schler, 2009, Abbasi & Chen, 2008) treat the inverse problem on content alone. The combined problem in which structural residue in terminal content is the inferential signal is the lane the present review identifies.

The central claim of this section is that different structures should produce different distributions of fidelity loss, accuracy loss, compression, synthesis, redundancy, distortion, and recoverable residue. Whether those differences are large enough to discriminate among generating structures from terminal messages is an empirical question, and it is the empirical core of the proposed research program.

---

## 4. Residue: How Production Histories Become Visible in Messages

This is the load-bearing theoretical section of the review. It develops a theory of *residue*, by which we mean an observable feature of a received message that carries information about its hidden production or transmission history. A residue can be lexical (an evidential marker, a hedge), syntactic (a reported-speech construction), pragmatic (an alignment formula, a stance act), distributional (compression or omission patterns relative to a baseline), or structural-stylistic (signs of synthesis across multiple inputs, or signs of linear relay degradation). Residues are probabilistic traces. Some are diagnostic, some are confounded, some are easily spoofed, and some appear only at population scale.

### 4.1 Evidentiality, source marking, and grammatical encoding of provenance

Roughly a quarter of the world's languages obligatorily mark every declarative utterance for *how the speaker knows* (Aikhenvald, 2004, Chafe & Nichols, 1986, Willett, 1988). The grammatical category of evidentiality distinguishes direct perception, inference, hearsay, and report (Tariana, Tuyuca, Cuzco Quechua, Tibetan varieties, and the Japanese suffix system are among the canonical cases). Aikhenvald (2004, 2018) and Willett (1988) provide the typology. Faller (2002) shows that reportives in Cuzco Quechua *suspend* speaker commitment rather than weaken it, a distinction that matters for theories of evidential responsibility. Squartini (2001) and Mushin (2001) extend the analytic to Romance and to narrative retellings, distinguishing evidentiality as a grammatical category from epistemological stance as a discourse-level orientation. The implication for the present project is that human linguistic systems have already evolved obligatory machinery for encoding the *transmission history* of a proposition. Where such machinery is grammatical, residue is rich and densely marked. Where it is only lexical (as in English), residue is sparser, optional, and confoundable with stylistic preference.

In languages without grammaticalized evidentials, stance and uncertainty are nonetheless marked through lexical and adverbial means. Biber and Finegan (1989) provide the canonical corpus-derived inventory of English stance markers across twelve semantic categories. Chafe (1986) shows that even conversational and academic English deploy evidentiality strategies pervasively. Hyland (1998) demonstrates that academic genres rely on hedging as an obligatory move that signals epistemic responsibility and recruits reader assent. Du Bois (2007) reframes stance as a triangulated act in which a subject evaluates an object, positions self, and aligns with another subject. Lakoff (1973) anchors the formal-semantic analysis of hedges as fuzzy-set markers. These lexical stance systems are the most accessible English-language residue surface for receivers without privileged access to a speaker's epistemic state.

Computational detection of these markers exists but is uneven. The BioScope corpus (Vincze, Szarvas, Farkas, Móra, & Csirik, 2008) and the CoNLL-2010 shared task (Farkas, Vincze, Móra, Csirik, & Szarvas, 2010) provide annotated training data for hedge cues and their scope. Committed-belief annotation (Diab et al., 2009, Prabhakaran, Rambow, & Diab, 2010) is the closest mainstream NLP analog to computational evidentiality. Stance detection (Mohammad, Kiritchenko, Sobhani, Zhu, & Cherry, 2016, Augenstein, Rocktäschel, Vlachos, & Bontcheva, 2016, Zubiaga et al., 2018) treats stance as a sentence- or document-level classification target. These computational traditions operationalize many of the distinctions named in the linguistic literature, but they typically do not treat the joint recovery of source, commitment, and transmission path as a unified inference problem.

### 4.2 Reported speech, testimonial distance, and the production format

A second class of residue concerns the marking of *another voice* within a received message. Vološinov (1929/1973) inaugurated the analytic tradition by showing that the grammatical envelope around reported speech (direct, indirect, free indirect) is ideological, encoding social-evaluative distance from the embedded voice. Bakhtin (1981, 1986) developed heteroglossia and double-voiced discourse as concepts that treat every utterance as carrying traces of others' words. Goffman (1981) decomposed the speaker role into *animator* (who voices), *author* (who composed), and *principal* (who is committed), so that a single sentence may flag distinct production-format origins. Clark and Gerrig (1990) reframe quotation as *demonstration* rather than description, with the quoter selectively depicting features of voice, register, and persona of the prior speaker. Vandelanotte (2009) and Tannen (1989) develop the typology of distancing indirect speech and "constructed dialogue," documenting cue inventories (tense shift, deictic shift, hedges like *like*, *goes*, *was all*, prosodic mimicry in transcribed speech) that constitute recoverable signatures of testimonial structure.

These literatures supply the residue analytics for a class of phenomena that is central to the present program. When a relayed message carries another voice, the form in which the voice is reported is informative about the relayer's relation to the source. A direct quotation with high specificity and integrated prosodic cues signals close access. An indirect summary with abstracted content and shifted deixis signals greater distance. A hearsay particle ("they say") signals minimum commitment. A free-indirect construction blends the voices in ways that can mark either ironic distance or sympathetic identification.

### 4.3 Pragmatic responsibility, commitment, and the norm of assertion

Linguistic markers of source and stance do not exhaust the residue space. They modulate the speaker's *commitment* to the propositional content, and this commitment is a normative object. Grice's (1975) maxim of Quality establishes the default that speakers are accountable for the truth of what they say. Brandom (1994) formalizes assertion as the undertaking of a public commitment that alters a ledger of entitlements and inferential consequences. Hearsay or echoic markers explicitly downgrade the ledger entry. MacFarlane (2011) and Williamson (2000) debate the norm of assertion (knowledge, truth, or retractable commitment), and Sperber and Wilson (1995, Wilson & Sperber, 2012) distinguish *descriptive* from *interpretive* use of representations, with the latter explicitly representing another representation rather than a state of the world. Recanati (2000) develops the metarepresentational structure of attitudes toward content. Murray (2014) provides a formal-semantic account of how evidentials contribute as not-at-issue updates rather than as part of the at-issue commitment. For the present project, these accounts specify what residue-bearing markers *do* normatively, and therefore what a receiver must infer when they appear or are conspicuously absent.

### 4.4 Stylistic leakage and role-specific language

Stylometric work (Mosteller & Wallace, 1964, Stamatatos, 2009, Juola, 2008, Koppel, Schler, & Argamon, 2009, Argamon et al., 2009, Abbasi & Chen, 2008) establishes that text leaks demographic and social-position attributes at accuracies of seventy-five to ninety-four percent under favorable conditions, with adversarial stylometry (Brennan, Afroz, & Greenstadt, 2012) defining the robustness limit. Computational sociolinguistics (Nguyen, Doğruöz, Rosé, & de Jong, 2016) provides the broader framework. Bramsen, Escobar-Molano, Patel, and Alonso (2011) demonstrate that superior-subordinate language patterns are extractable from organizational corpora such as Enron. Eckert (2008) develops the *indexical field* analytic, which treats stylistic features as variably interpretable indexes whose meaning depends on the configuration of features present and on receiver competence. These residue sources are continuous, ubiquitous, and probabilistic. They are also the residue type most studied at scale.

### 4.5 Genre, bureaucratic compression, and resemiotization

Genre theory contributes residue analytics that are missing from the stylometric tradition. Genres are typified rhetorical actions in response to recurrent situations (Yates & Orlikowski, 1992, 2002, Bazerman, 1988). They are also routes by which institutional structure shapes the form of any message produced under them. Iedema's (2001, 2003) concept of *resemiotization* identifies a specific transformation type that is central for residue theory: as content moves through bureaucratic hierarchies it is repeatedly recoded into more abstract, more durable, and more institutionally legible forms, and each transformation systematically strips local indexicality while inscribing institutional indexicality. The residue of resemiotization is a particular kind of compression and a particular kind of stance neutralization. Power (1997) and Star and Strauss (1999) show that what is erased is articulation work, repair, and local negotiation, while what is inscribed is verification ritual and formal authorization. The implication is that bureaucratic relay produces a recognizable signature in terminal artifacts. The signature is partly diagnostic (genre conventions, formulaic templates, citation patterns) and partly destructive of upstream residue.

### 4.6 Rumor morphology

Rumor research provides a fifth residue inventory. Allport and Postman's (1947) triad (leveling, sharpening, assimilation) describes residue-relevant transformations that accumulate across hops. Knapp (1944), Buckner (1965), Shibutani (1966), Rosnow (1988, 1991), and DiFonzo and Bordia (2007a, 2007b) develop the typology of mutations under transmission and identify the structural conditions under which expansion versus contraction is the dominant tendency. The rumor literature is methodologically conservative on receiver inference (it concerns transmission dynamics rather than provenance reconstruction from terminal artifacts), but it provides the catalog of mutation processes whose residues a legibility theory must accommodate.

### 4.7 Synthesis, linear relay, clustered reinforcement, and laundering

A residue inventory should also catalog signs of process types that cannot be read off a single lexical marker but appear at the message level or across multiple messages. Plausible candidates include the following. Signs of *synthesis* across multiple inputs (mixed register, reconciled contradictions, lossy integration of details with different evidential pedigrees, citation-style listings) suggest a central node aggregating from heterogeneous sources. Signs of *linear relay degradation* (cumulative omission, drift toward gist and emotional salience, accumulating compression) suggest a chain. Signs of *clustered reinforcement* (high inter-message similarity across apparently independent paths, repeated formulae, identical detail-sets) suggest local echo or coordinated production. Signs of *independent corroboration* (overlapping content with non-overlapping wording, complementary evidence, divergent stance) suggest independent paths converging on a target. Signs of *adversarial laundering or source obfuscation* (genre shift across implausible boundaries, voice-mismatch, stripped-out indexicality, persona-inconsistent stylistic features) suggest deliberate provenance suppression. These residues are *configurational* rather than punctual. They depend on the receiver having access to either multiple messages, a baseline expectation about plausible production processes, or comparison material from other paths. They are the residues that distinguish *what kind of structure* produced the message, when the receiver cannot identify the exact source.

### 4.8 Discriminative versus detectable: the two conditions of legibility

Two conditions must hold for residue to confer structural legibility. The residue must be *detectable* by the receiver, in the sense that the relevant feature is present in the artifact and recoverable from it. The residue must also be *discriminative* across alternative production histories, in the sense that the conditional distribution of the feature differs sufficiently across plausible histories that the receiver can update meaningfully between them. A detectable but non-discriminative residue is uninformative. A discriminative but undetectable residue is wasted information. Both conditions can fail under adversarial conditions, when an adversary deliberately spoofs a residue, and both can fail under bureaucratic compression, when resemiotization strips diagnostic indexicality without leaving a visible trace of the stripping.

The central claim of this section is that structural legibility depends on whether transformation leaves residue that is both detectable and discriminative across alternative production histories. This claim is empirical, not analytic. Whether a given communication structure produces legible residues, for a given content type, for a given receiver class, is an open question that the proposed research program is positioned to investigate.

---

## 5. Receiver Inference Over Hidden Communicative Histories

Receivers do not assess accuracy from content alone. They infer hidden histories, which is to say they infer who likely produced the message, what that producer had access to, what incentives they had, what transformations the message underwent, and what distortions are likely. The literatures that bear on this inference span memory psychology, social-evolutionary psychology, philosophical epistemology, intelligence analysis, forensic deception, and Bayesian evidence aggregation.

### 5.1 Source monitoring and reality monitoring

The *source-monitoring framework* (Johnson, Hashtroudi, & Lindsay, 1993, Mitchell & Johnson, 2000, 2009, Lindsay & Johnson, 1989, Johnson, 2006) treats memory not as veridical retrieval but as an attribution process. At retrieval, the rememberer uses heuristic and systematic decision processes over phenomenal characteristics of a trace (perceptual detail, contextual specificity, cognitive operations, affective tone) to infer where a representation came from. The framework supplies the canonical cognitive architecture for a class of inferences that is structurally analogous to the legibility problem. Receivers reading a message face an attribution problem: they project features of the message back onto a latent space of possible communicative origins (first-hand versus relayed, experienced versus imagined, sincere versus instructed). Source-monitoring errors (misattribution, cryptomnesia, suggestibility) arise when traces from different sources overlap on diagnostic features. The framework's central claim, that featural diagnosticity is the lever by which receivers recover histories, is directly portable to the legibility setting.

*Reality monitoring* originated as an intrapersonal operation (Johnson & Raye, 1981) but has been reweaponized as an interpersonal forensic test. Sporer (1997, 2004, 2016), Masip, Sporer, Garrido, and Herrero (2005), and Vrij (2008, 2015) and colleagues have shown that fabricated accounts show systematically fewer perceptual, contextual, spatial, and temporal details and more cognitive-operation markers than truth-tellers, with above-chance but criterion-unstable separability. The Vrij-Granhag cognitive-load program (Vrij et al., 2008) makes the encoding/retrieval process itself manipulable, amplifying the structural differences between two latent histories. For the present project, this literature provides the empirical proof-of-concept that text alone carries recoverable traces of whether the producer experienced or invented the referent, and it operationalizes a trace inventory (sensory, contextual, temporal, affective, cognitive-operation markers) that a theory of receiver inference can audit.

### 5.2 Epistemic vigilance and philosophical testimony

The *epistemic vigilance* program (Sperber et al., 2010, Mascaro & Sperber, 2009, Mercier, 2020, Mercier & Sperber, 2017) operationalizes receiver monitoring at the cognitive level. Sperber and colleagues argue that humans have evolved a layered apparatus that vigilates *source* (who is speaking, with what competence and benevolence) and *content* (does it cohere with prior beliefs, does the argument hold up). Mercier's *Not Born Yesterday* synthesizes the cognitive-science case against the easy-gullibility folk theory, arguing that open vigilance mechanisms compute multi-cue assessments before updating. Developmental work (Koenig & Harris, 2005, Harris & Corriveau, 2011, Clément, 2010) shows that selective trust is online by age three to four, with preschoolers tracking informant accuracy history and weighting cultural standing.

The philosophical-testimony literature provides the normative scaffolding. Coady (1992), Burge (1993), Hardwig (1985), Fricker (1994), Lackey (2008), and Goldberg (2007) debate whether testimony is a basic source of warrant or whether the hearer must inferentially earn the warrant by monitoring speaker reliability. Lackey's dualism (both speaker and hearer contribute positive epistemic work, and testimony can *generate* knowledge rather than only transmit it) is the most useful position for the present program, because it permits the message itself to carry warrant-relevant structure independent of speaker first-person knowledge. The Sperber-Mercier program and the philosophical-testimony literature together supply the receiver-side architecture: receivers should be doing inference over latent communicative histories with separate calibration of source and content channels.

### 5.3 Intelligence analysis, credibility assessment, and the two-axis representation

The intelligence-analysis tradition is the institutionalized analog of the cognitive and philosophical work above. Heuer's *Psychology of Intelligence Analysis* (1999) and Heuer and Pherson's *Structured Analytic Techniques* (2019) operationalize Analysis of Competing Hypotheses (ACH) as the field's closest thing to a formal evidential calculus. Kent's (1964) "Words of Estimative Probability" framed the verbal-versus-numeric debate. Mandel and Barnes (2014) and Mandel (2015, 2021) provide empirical anchors for forecast calibration. Friedman and Zeckhauser (2012, 2015) distinguish likelihood from confidence and argue for numeric or numeric-anchored expressions. Tetlock and Gardner (2015) and Mellers et al. (2014, 2015) establish that trained-and-aggregated forecasters reach Brier scores around 0.20 on geopolitical questions. The NATO Admiralty Code (AJP-2.1 / STANAG 2511, see References to Verify) is a formal grid that decouples source reliability (A-F) from information credibility (1-6) and forces analysts to encode them separately, exactly the two-channel architecture the cognitive and philosophical literatures theorize.

Forensic deception research provides the empirical ceiling. Bond and DePaulo (2006) meta-analyze 206 studies and 24,483 judges, finding 54% accuracy without aids. DePaulo et al. (2003) catalog 158 cues and conclude there is no Pinocchio's-nose. Vrij (2008) and Vrij, Granhag, and Mann (2011) shift the field toward active interview techniques. Newman, Pennebaker, Berry, and Richards (2003), Tausczik and Pennebaker (2010), and Hancock, Curry, Goorha, and Woodworth (2008) develop the LIWC linguistic fingerprint of deception, with accuracies in the high sixties under controlled conditions and sharp dependence on medium and topic. Eyewitness research (Loftus & Palmer, 1974, Wells & Olson, 2003, Wells, Memon, & Penrod, 2006) catalogs the failure modes of receiver calibration in legal-institutional settings.

### 5.4 Bayesian evidence aggregation and strategic communication

A formal-probabilistic tradition (Schum, 1994, Kadane & Schum, 1996, Tecuci, Schum, Marcu, & Boicu, 2016) develops evidential Bayesian networks for legal and intelligence reasoning, explicitly bridging messy real-world evidence to formal probability. A game-theoretic tradition (Crawford & Sobel, 1982, Kamenica & Gentzkow, 2011, Bergemann & Morris, 2019) treats communication as strategic. Crawford and Sobel's cheap-talk equilibria show that when sender and receiver preferences diverge, only partition information is transmitted. Kamenica and Gentzkow's Bayesian-persuasion result shows that when the sender has commitment power, the *distribution* of messages is informative. Bergemann and Morris's information-design framework unifies these results. For the present project, the strategic-communication tradition specifies the upper bound on what residue alone can tell a receiver about an adversarial sender's underlying state, and the evidential-Bayesian-network tradition specifies the formal inference machinery that aggregates the residues once recovered.

The central claim of this section is that accuracy judgment is an inference over a partially observable communicative process. Receivers do not read accuracy off content. They reconstruct, from residue and prior knowledge, hypotheses about who produced the message and how, and they update accuracy beliefs in light of those reconstructions. The quality of the reconstruction is the legibility problem.

---

## 6. LLMs as Receivers, Relays, and Evaluators

LLMs are now a theoretically consequential class of receivers. They perform summarization, triage, analytic synthesis, credibility assessment, and communication relay at scale in applied settings, and they participate in synthetic social systems whose dynamics are an object of study in their own right. Their relevance to the present program is fourfold. They are *mutation engines* whose transformations of content under transmission can be instrumented under known ground truth. They are *receivers* whose inferences over residue can be elicited and compared across information regimes. They are *evaluators* whose judgments of fidelity and accuracy can be measured against ground truth. They are *inferred-provenance generators* whose reconstructions of communicative history can themselves be examined for systematic bias and plausibility-versus-validity dissociation. The four uses must be kept distinct.

### 6.1 LLMs as mutation engines and as participants in transmission chains

The generative-agents tradition (Park, O'Brien, Cai, Morris, Liang, & Bernstein, 2023, Park et al., 2022, 2024) and the LLM-ABM literature (Argyle, Busby, Fulda, Gubler, Rytting, & Wingate, 2023, Aher, Arriaga, & Kalai, 2023, Horton, Filippas, & Manning, 2023, Manning, Zhu, & Horton, 2024) established LLMs as agent components in social simulations. Domain-relevant subwork has examined LLM-driven news diffusion (Liu, Yan, Chen, Liu, & Yang, 2024), opinion dynamics (Chuang, Goyal, Harlalka, et al., 2024), echo chambers (Lu et al., 2025), rumor spreading (Liu, Wang, et al., 2025), stepwise deception and semantic drift (Li et al., 2024), and topology-conditioned multi-agent information propagation (Qiu et al., 2025).

Direct evidence that LLM transmission preserves systematic content biases comes from Acerbi and Stubbersfield (2023), who showed that single-LLM serial reproduction exhibits the same content biases as human chains. Perez et al. (2024) extended this to LLM-to-LLM iterated transmission, documenting cumulative drift toward attractor states whose strength varies by content property and prompt openness. Brinkmann et al. (2023) frame the broader phenomenon as *machine culture*. Population-scale dynamics under recursive training of generative models on their own outputs produce *model collapse* (Shumailov, Shumaylov, Zhao, Papernot, Anderson, & Gal, 2024) and self-consuming generative failure (Alemohammad et al., 2024), with progressive loss of distributional tails and diversity. Multi-agent LLM systems fail in catalogable ways traceable to unstructured natural-language communication between agents (Cemri et al., 2025). These results are central to the present program because they establish that LLMs in transmission chains transform content according to recoverable regularities and also accumulate biases that can be modeled.

### 6.2 LLMs as judges, evaluators, and credibility assessors

The LLM-as-judge paradigm (Zheng et al., 2023, Liu, Iter, Xu, Wang, Xu, & Zhu, 2023) treats LLMs as scalable evaluators of model outputs. Empirical work shows that strong LLM judges agree with human preferences at rates approaching inter-human agreement, but with systematic biases: position bias and verbosity bias (Wang et al., 2024), familiarity and self-recognition bias (Panickssery, Bowman, & Feng, 2024, Stureborg, Alikaniotis, & Suhara, 2024), and stylistic priors carried in from training. Constitutional AI and RLHF (Bai et al., 2022) shape these judgments in ways that interact with the truthful-prior dynamics noted in §6.4. Applied to fact-checking and claim verification (Hoes, Altay, & Bermeo, 2023, Quelle & Bovet, 2024), LLM judges show moderate accuracy with pronounced sensitivity to retrieval context and claim language. For the present project, this literature establishes that LLM judgments of credibility and accuracy are not neutral readings of content. They are reconstructive acts with structural biases of their own, and they leave systematic fingerprints in their assessments.

### 6.3 LLM calibration, uncertainty, hallucination, and source attribution

Kadavath et al. (2022) show that larger LLMs are reasonably calibrated when forced to verbalize P(True) on their own answers, and Tian, Mitchell, Zhou, Sharma, Rafailov, Yao, Finn, and Manning (2023) show that verbalized confidence from RLHF-tuned models is often better calibrated than token-level probabilities. Zhou, Jurafsky, and Hashimoto (2023) reveal the converse: LLMs are sensitive to epistemic markers (hedges, factive verbs, certainty adverbs) in incoming messages but interpret them as distributional cues rather than as transmission signals about communicative history. Lin, Hilton, and Evans (2022) introduce TruthfulQA, documenting systematic susceptibility of LLMs to human-style falsehoods. Hallucination surveys (Ji et al., 2023, Zhang et al., 2023) catalog the failure modes of grounded generation. Retrieval-augmented generation and attributed question answering (Gao, Xiong, et al., 2023, Bohnet et al., 2022, Gao, Yen, Yu, & Chen, 2023) and atomic-fact evaluation (Min et al., 2023) show that even scaffolded LLMs produce long-form text in which a significant fraction of claims lack adequate citation support. These results establish that LLM receivers *do* read pragmatic residue, including hedges, evidentials, and citation patterns, but they interpret residue as distributional rather than transmissive, and they reconstruct plausible source-grounded narratives that may pass surface checks while only partially preserving the actual epistemic chain.

### 6.4 LLMs as inferred-provenance generators

A more recent body of work tests LLMs as authorship-attribution and source-inference engines. Huang, Chen, and Shu (2024a, 2024b) show that LLMs perform zero-shot authorship attribution that exceeds fine-tuned BERT baselines, leveraging stylometric residue without explicit feature engineering. Accuracy degrades sharply with the number of candidate authors, and attribution inherits training-data biases. LLM-versus-LLM detection (Mitchell, Lee, Khazatsky, Manning, & Finn, 2023, Hans et al., 2024) achieves high AUROC under controlled conditions but faces an impossibility result under paraphrase attack (Sadasivan, Kumar, Balasubramanian, Wang, & Feizi, 2023). Watermarking (Kirchenbauer, Geiping, Wen, Katz, Miers, & Goldstein, 2023) injects an active recoverable trace at generation time. Membership-inference and training-data-provenance probes (Shi et al., 2024, see References to Verify) attempt to recover whether a given text was in the model's training data. For the present project, this literature establishes that LLM receivers are partial provenance readers: they extract real residue (stylistic, distributional, probability-curvature) but also produce confidently wrong attributions when residue has been laundered or when the candidate space exceeds their effective discrimination capacity.

### 6.5 Skepticism: machine bias, caricature, sycophancy, and homogeneity

A skeptical literature has crystallized in parallel. Machine bias (Boelaert, Coavoux, Ollion, Petev, & Präg, 2025, Bisbee, Clinton, Dorff, Kenkel, & Larson, 2024) documents that LLM survey response distributions diverge systematically from human populations. Caricature (Cheng, Durmus, & Jurafsky, 2023) and Marked Personas (Cheng, Piccardi, & Yang, 2023) document that LLM persona simulations exaggerate stereotypical features of marginal identities. Sycophancy (Sharma et al., 2024, Perez et al., 2023) and social-desirability bias (Salecha, Ireland, Subrahmanian, et al., 2024) document that LLMs adjust their outputs to perceived interlocutor preferences. Homogeneity collapse and emergent collective bias (De Marzo, Pietronero, et al., 2025) document that LLM populations converge on shared conventions and shared biases. Validation circularity (Larooij & Tornberg, 2025) and causal-inference critiques (Wang et al., 2023) catch the field's most common methodological errors. Persuasion experiments (Salvi, Horta Ribeiro, Gallotti, & West, 2025) show that LLMs can shift human beliefs with high efficacy. The skeptical literature is essential for the present program because it constrains the inferences that can be drawn from LLM-receiver judgments to claims about LLMs themselves rather than direct claims about humans.

### 6.6 Distinguishing the four LLM roles

The four roles introduced at the start of this section are routinely conflated in the empirical literature, and conflation produces fragile inference. The proposed program treats them as distinct experimental positions.

*LLMs as mutation engines* are used to instrument the transformation channel under known ground truth, with the LLM not asked to judge or attribute, only to relay or rewrite.

*LLMs as receivers* are presented with terminal messages under varied information regimes and asked to produce inferences over communicative history. Their inferences are an object of study.

*LLMs as evaluators of fidelity* are presented with paired (original, terminal) messages and asked to measure semantic preservation. Their evaluations are validated against multiple metrics.

*LLMs as judges of likely accuracy* are presented with messages, plus varying levels of history, and asked to estimate the probability that the claim corresponds to the world. Their judgments are calibrated against ground truth.

*LLMs as inferred-provenance generators* are presented with terminal messages and asked to reconstruct the production history. Their reconstructions are the target of plausibility-versus-validity dissociation tests.

The central claim of this section is that LLMs may be unusually sensitive to semantic and pragmatic residue because of their broad language priors, but they may also generate plausible but spurious reconstructions of communicative history. The conditions under which these two tendencies dominate are an empirical question, and they are central to the proposed program.

---

## 7. Locating the Contribution

The proposed contribution sits at the intersection of several mature literatures. This section identifies the closest neighbors and specifies what each contributes and what each does not address.

### 7.1 Communication theory and CCO

Communication theory in the Bakhtin-Goffman-Vološinov-Clark-Gerrig tradition and CCO theory in the Taylor-Cooren-McPhee-Ashcraft tradition explain a great deal about message transformation, genre, stance, production format, and the constitutive role of communication in institutional life. They develop the theoretical vocabulary (animator/author/principal, ventriloquism, resemiotization, double-voiced discourse, stance triangulation) that the residue analytics in §4 require. They do not generally produce computationally testable predictions about how structural variation maps to recoverable residue in terminal messages, and they do not engage with LLMs as receivers or as transmission media. The present program contributes the missing empirical bridge while drawing on the conceptual vocabulary these literatures supply.

### 7.2 Network science and network epistemology

Network science and network epistemology (Centola, Watts, Zollman, Lazer-Friedman, Golub-Jackson, Becker-Centola, Mason-Watts) explain a great deal about diffusion, collective inference, topology, redundancy, clustering, centralization, and the conditions under which connected populations converge on truth. They have not typically examined the *semantic residues* that topology leaves in terminal messages, because they treat the propagated item as an opaque token. They also do not usually consider receiver inference over hidden communicative histories. The present program contributes a content-coupled extension of the inverse-inference problem, in which residue in terminal content rather than timing of arrival is the inferential signal.

### 7.3 Serial reproduction, rumor, and cultural transmission

Serial reproduction (Bartlett), rumor research (Allport-Postman, Knapp, Caplow, Shibutani, Buckner, Rosnow, DiFonzo-Bordia), and cultural transmission (Mesoudi-Whiten, Kashima, Acerbi-Stubbersfield) explain mutation under transmission, with detailed accounts of leveling, sharpening, assimilation, gist preservation, schema-consistent distortion, and emotional salience. These literatures have not typically engaged non-linear network structures, do not generally pose the receiver-inference question, and have only recently incorporated LLMs as either transmitters or receivers. The present program contributes the receiver-inference framing on top of the mutation analytics these literatures supply, and it generalizes serial-reproduction designs to networked transmission with continuous-text content.

### 7.4 Computational sociolinguistics, stylometry, and forensic linguistics

Computational sociolinguistics, stylometry, and forensic linguistics (Stamatatos, Argamon, Abbasi, Brennan-Afroz-Greenstadt, Coulthard, Nguyen et al., Bramsen et al.) explain a great deal about social, authorial, and role traces in language, with documented accuracies for demographic and authorship inference. They have not typically been coupled to propagation structure, do not generally infer transmission history from textual residue, and operate primarily at the level of a single producer rather than across a chain. The present program contributes a propagation-aware extension of stylometric and sociolinguistic inference, in which the inferential target is not authorship of a single text but the structural process that produced its terminal form.

### 7.5 Intelligence analysis and social epistemology

Intelligence analysis (Heuer, Mandel, Tetlock, Friedman-Zeckhauser, Schum, Kadane-Schum, Tecuci) and social epistemology (Sperber et al., Mercier, Coady, Burge, Hardwig, Fricker, Lackey, Goldberg) explain a great deal about credibility, testimony, evidence aggregation, source reliability, calibration, and the institutional management of uncertainty. They have not typically been integrated with computational measurement of structural residue, and they do not address LLMs as receivers. The present program contributes a setting in which their constructs can be made empirically tractable under known ground truth and where receivers themselves can be experimentally manipulated.

### 7.6 LLM and AI-mediated communication

LLM research (Park, Argyle, Aher, Horton, Tornberg, Chuang, Liu, Qiu, Acerbi-Stubbersfield, Perez, Brinkmann, Zheng, Kadavath, Tian, Huang, Mitchell, Sadasivan, Kirchenbauer, Shumailov, Cemri) explains a great deal about LLM judgment behavior, simulation fidelity, hallucination, calibration, source attribution, summarization, and synthetic-social-system dynamics. It does not yet articulate structural legibility as a *theory of communication*, and it generally treats LLMs as the object of study rather than as instruments for studying communication. The present program contributes the theoretical reframe and the experimental design that uses LLMs as the empirical laboratory for a communication-theoretic question.

### 7.7 The unoccupied intersection

The unoccupied intersection is not "no one has studied this." It is more specific. It is the intersection of: (1) structure-conditioned message transformation, (2) recoverable residue or structural legibility, (3) receiver inference over hidden communicative histories, and (4) LLM-based computational instantiation in which both the mutation channel and the receiver can be experimentally manipulated under known ground truth. Each of the four components has neighbors. None of the existing neighbors occupies the intersection.

A useful three-layer architecture for thinking about this contribution distinguishes *legacy theory*, *computational bridge*, and *LLM instantiation*. Legacy theory comprises the human and organizational literatures on serial reproduction, source monitoring, credibility, diffusion, testimony, evidentiality, genre, rumor, and intelligence. Computational bridge comprises network models, stylometry, NLP-based stance and hedge detection, source localization, social signal extraction, and pre-LLM simulation. LLM instantiation comprises LLMs as receivers, relays, summarizers, evaluators, mutation engines, and provenance reasoners. The proposed program is a communication and network theory paper whose empirical laboratory uses LLMs. It is not an LLM paper with background, and it is not an applied intelligence tool.

---

## 8. Toward a Theory of Structural Legibility

The review motivates a small set of propositions. Each is stated precisely, given a mechanism, and accompanied by at least one empirical implication.

**P1. Communication structures systematically shape message transformation.**
*Mechanism.* Different structural configurations (chain, hub-and-spoke, all-channel, clustered, hierarchical) impose different role allocations, redundancy regimes, compression points, and synthesis demands on the messages they carry, and these in turn produce different distributions of preservation, distortion, omission, addition, and integration. *Empirical implication.* Holding source content and content type fixed, the distribution of terminal-message features across messages produced by different structures should be statistically distinguishable at the population level.

**P2. Message transformations differ in their residue profiles.**
*Mechanism.* Compression, synthesis, linear relay, clustered reinforcement, and adversarial laundering leave qualitatively different traces in terminal messages, including lexical (evidential and stance markers), syntactic (reported-speech constructions), pragmatic (alignment cues, hedging patterns), distributional (omission and addition profiles), and configurational (cross-message similarity patterns) traces. *Empirical implication.* The conditional distribution of residue features differs across transformation types, with sufficient discriminability to permit better-than-chance classification of transformation type from residue alone in at least some structural conditions.

**P3. Structural legibility varies by topology, task, content type, redundancy, source heterogeneity, role differentiation, and compression point.**
*Mechanism.* Legibility is the joint product of detectability (the residue is present in the artifact and recoverable from it) and discriminability (the residue separates plausible histories). Both conditions are sensitive to the upstream production conditions and to the receiver's prior knowledge of plausible alternatives. *Empirical implication.* Legibility should be measurable as a graded property of (structure, content, receiver-prior) triples, with characteristic peaks and troughs across the design space.

**P4. Structural legibility is distinct from accuracy and from fidelity.**
*Mechanism.* Legibility concerns the message-process relation. Accuracy concerns the message-world relation. Fidelity concerns the message-message relation. The three can vary independently. A structure may produce accurate messages that are not legible (the inference about how the message was produced is not recoverable). A structure may produce legible messages that are inaccurate (the production process is recoverable and reveals systematic distortion at the source). *Empirical implication.* In a sufficiently varied experimental design, the empirical correlation among legibility, fidelity, and accuracy should be moderate rather than near-unity, with identifiable cells of the design where they dissociate.

**P5. Receiver judgments of accuracy are mediated by inferred communicative history.**
*Mechanism.* Receivers do not read accuracy directly from content. They reconstruct, from residue and prior knowledge, hypotheses about who produced the message and how, and they update accuracy beliefs in light of those reconstructions. The intermediate inference is the bottleneck. *Empirical implication.* Manipulations of information regime that change the inferred-history distribution but leave content unchanged should change accuracy judgments. Manipulations of content that leave the inferred-history distribution unchanged should change accuracy judgments less.

**P6. LLM receivers may exploit some residues better than humans, but may also over-infer coherent histories from weak cues.**
*Mechanism.* LLM language priors are sensitive to fine-grained pragmatic and stylistic features that humans process implicitly and inconsistently. The same broad priors that enable detection also impose plausibility biases that favor coherent reconstructions over fragmented ones, even when the residue does not support coherence. *Empirical implication.* In conditions where the residue is sparse or ambiguous, LLM receivers should produce more confident and more coherent provenance reconstructions than the residue licenses, with plausibility-versus-validity dissociation visible against ground truth.

**P7. Access to communicative history should improve calibration more than raw accuracy when terminal content is plausible but historically degraded.**
*Mechanism.* When a message is fluent, coherent, and genre-consistent but the production process was lossy or distorting, raw accuracy judgments default to plausibility. Access to history (path metadata, intermediate versions, competing variants) disrupts the plausibility default and forces explicit evidential aggregation, which typically lowers confidence and improves calibration. *Empirical implication.* In high-plausibility low-fidelity cells, adding history should reduce both stated confidence and judgment error, with the calibration gain exceeding the raw-accuracy gain.

**P8. Some structures may produce both higher accuracy and higher legibility. Others may produce high accuracy but low legibility, or low accuracy but high legibility.**
*Mechanism.* Accuracy depends on source access, source competence, and transmission fidelity. Legibility depends on the survival of process-diagnostic residue in the terminal form. The two are governed by partly different mechanisms. Bureaucratic synthesis structures may produce accurate consolidated outputs whose internal heterogeneity and intermediate steps are dissolved (high accuracy, low legibility). Chain structures with heavy degradation may produce inaccurate outputs whose chain-of-relay signature is highly recoverable (low accuracy, high legibility). *Empirical implication.* A two-dimensional scatter of (legibility, accuracy) across structural conditions should show non-trivial spread, with examples of each combination.

These propositions are not mutually independent. P3 specifies how P1's structural effect is mediated. P4 separates the constructs that P5 and P7 then relate at the receiver level. P6 is specific to the LLM-receiver class introduced in §6. P8 makes explicit a possibility that the prior instrument-facing framing implicitly excluded by treating accuracy as the target estimand.

---

## 9. Empirical Implications for an LLM-Based Computational Experiment

The propositions in §8 are theoretical claims about communication. They become empirically tractable when paired with an experimental setup in which the production process is controlled and the receiver's information regime is manipulable. This section sketches such a setup without proposing a complete instrument.

The core design pairs a *generation pipeline* with a *receiver pipeline*. The generation pipeline produces messages with known ground truth and traverses them through varied communication structures. The receiver pipeline presents the resulting artifacts to LLM receivers under varied information regimes and elicits judgments over multiple targets.

Generation has the following components. (a) Original messages with known ground truth, varying in content type (descriptive, evaluative, narrative, technical, evidential), specificity, and source-perspective. (b) Communication structures, varying along the dimensions identified in §3: chain, hub-and-spoke, clustered, all-channel, hierarchical, mixed. (c) LLM agents that transform, summarize, relay, synthesize, or distort messages at each node, with role-conditioned and structurally-conditioned mutation regimes. (d) Full retention of ground truth at every stage: original message, world state, path, intermediate versions, source position, structural condition, and final received form.

The receiver pipeline presents terminal messages to receivers under varied *information regimes*. The seven regimes proposed are:

1. Terminal message only.
2. Terminal message plus source description.
3. Terminal message plus structural origin label (chain, hub, cluster, hierarchy).
4. Terminal message plus path metadata (hop count, timing, intermediate position counts).
5. Terminal message plus intermediate versions.
6. Terminal message plus competing variants from different paths.
7. Full communicative history.

Receivers are asked to produce judgments on:

1. Likely structural provenance or production regime.
2. Fidelity to the original message.
3. Likely accuracy with respect to ground truth.
4. Confidence on each judgment.
5. Explicit reasoning basis (which features the judgment relied on).

The theory predicts more than the naive monotonic claim that more information improves judgment. It predicts that different *kinds* of history information alter the inferential basis of the judgment in qualitatively different ways. Intermediate versions should reveal mutation trajectories that source descriptions and structural labels cannot. Competing variants from different paths should reveal whether apparent corroboration is independent or lineage-dependent. Path metadata should reveal redundancy and synthesis structure. Some information increments should lower confidence relative to terminal-message-only judgments, and this lowering may improve calibration even when it does not improve raw accuracy. These are testable predictions with characteristic signatures.

Five design conditions are non-optional given the methodological cautions accumulated in §6 and in the prior instrument-facing review. Multiple LLM model families should be used to prevent disagreement from collapsing into one model's decoding noise. Mutation regimes should be paired across content classes to prevent receiver inference from reading topic rather than structure. Adversarial and naive threat models should both be reported. Multiple semantic-fidelity metrics should be used in parallel rather than collapsed into a single composite. Identifiability tests should precede calibration claims, because reporting calibration on a non-identifiable target overstates achievable performance.

The empirical artifact this design produces is not a dashboard or an estimator. It is a matrix of (structural condition × information regime × judgment target) cells, with calibration and discrimination measurements per cell, and identifiability tests across cells. The matrix is theory-bearing because the propositions in §8 make differential predictions about which cells should show identifiability and which should not, which information increments should produce nonlinear calibration gains, and where accuracy and legibility should dissociate.

---

## 10. Research Questions and Hypotheses

The propositions and design above motivate the following research questions and hypotheses.

**Research questions.**

RQ1. Do different communication structures produce distinguishable residue profiles in terminal messages?

RQ2. Can LLM receivers infer structural provenance from terminal-message content alone?

RQ3. Which increments of communicative history most improve structural provenance judgments?

RQ4. Does inferred or supplied structural provenance improve LLM judgments of fidelity and accuracy?

RQ5. Are LLMs better at judging fidelity than accuracy under matched information conditions?

RQ6. Under what conditions do LLMs generate plausible but spurious provenance reconstructions?

RQ7. Do structures that produce more accurate messages also produce more legible messages, or do accuracy and legibility dissociate?

**Hypotheses.**

H1. Terminal-message-only judgments will recover *coarse production regimes* (chain versus hub versus cluster versus all-channel) better than they recover *exact structural origins* (which node within a structure).

H2. Mutation history (intermediate versions) will improve fidelity judgments more than source labels or static structural descriptions, because mutation trajectories supply direct evidence of transformation while labels supply only categorical priors.

H3. Path metadata and competing variants will improve calibration by revealing whether apparent corroboration is independent or lineage-dependent. The calibration gain will be larger in cells where naive plausibility cues point in the opposite direction from lineage structure.

H4. LLMs will overestimate accuracy when messages are coherent, specific, and genre-consistent but historically degraded, with the overestimation tracking the level of surface fluency rather than the level of preserved evidential grounding.

H5. Structural information will affect accuracy judgments primarily through inferred *source access*, *redundancy*, and *transmission loss*, with the path from structural label to accuracy judgment routed through an intermediate provenance inference.

H6. Some centralized synthesis structures will produce fluent and coherent messages that are *less* faithful to originals than chain-produced messages, making them high in plausibility but low in fidelity, and producing characteristic legibility losses for the consolidation step.

H7. Chain structures will produce more detectable degradation residues than some clustered or centralized structures, because cumulative drift along a single path accumulates correlated mutations that are statistically more distinctive than the rolled-up output of synthesis.

H8. Structural legibility and message accuracy will be empirically separable, with non-trivial spread across the (legibility, accuracy) plane in a sufficiently varied design.

The hypotheses are stated in a form that admits clear negative results. A finding that LLM receivers cannot recover coarse production regimes from terminal content (counter to H1) is publishable because it bounds the legibility of communication under the conditions tested. A finding that mutation history does *not* improve fidelity judgments more than labels (counter to H2) is publishable because it constrains the value of process information to receivers. The design is structured to make negative results informative rather than merely embarrassing.

---

## 11. Conclusion

This review reframes a research program. The prior framing asked whether the accuracy of an intercepted communication could be estimated from network-structural signals and calibrated in an LLM-powered laboratory. The revised framing asks how communicative structures transform messages, whether those transformations leave recoverable traces in terminal artifacts, and whether LLM receivers can use those traces to infer structural provenance, fidelity, and likely accuracy.

The theoretical contribution is a theory of *structural legibility* and the broader inference problem of *communicative recoverability*. The claim is that messages preserve probabilistic traces of the structures and transmission processes that produced them, that receivers' judgments of fidelity and accuracy depend on whether those traces are recoverable, and that legibility is a distinct construct that can dissociate from accuracy in directions that matter for both theory and practice. The methodological contribution is an LLM-based computational experiment that makes hidden communicative histories observable and manipulable, allowing the theoretical claims to be tested under known ground truth and across systematically varied information regimes.

The most natural primary audience for the paper is *computational social science*, which has methodological tools to engage the experimental design and venue conventions that admit theoretical contributions framed around new constructs. Two alternative audiences merit attention. *Communication theory and organizational communication* venues are well-positioned for the residue and CCO-adjacent material in §§3-5, with reduced emphasis on the LLM instantiation. *AI and society / NLP* venues such as workshops on LLMs as evaluators or as social-simulation media can host the §6 material with reduced emphasis on the legacy theory. Each positioning carries tradeoffs. Computational social science maximizes integrative reach but requires defending against both narrow communication-theoretic and narrow AI-evaluation critiques. The communication and organizational-communication positioning preserves theoretical depth but truncates the LLM experimental contribution. The AI positioning admits the experimental contribution most directly but risks reading as an LLM paper with background, the framing the present review explicitly resists.

Several constraints follow from the theoretical reframe. Structural provenance is not identical to identification of a specific group or person. Coherence is not accuracy. Plausibility is not validity. More information does not always increase confidence. Synthetic LLM simulations are not direct evidence about humans except under explicit qualification. Absence of LLM-specific prior work is not absence of theory, because the relevant mechanisms come from older literatures on human communication, organizations, rumor, testimony, pragmatics, and social cognition. These constraints are not boilerplate cautions. They are the substantive commitments that distinguish the proposed contribution from neighbors that share parts of its surface.

The intersection that this review identifies is not novel because no one has studied any of its components. It is unoccupied because no existing program combines structure-conditioned message transformation, recoverable residue, receiver inference over hidden communicative histories, and LLM-based computational instantiation in a single empirical and theoretical frame. That intersection is where the present program sits.

---

## References

Abbasi, A., & Chen, H. (2008). Writeprints: A stylometric approach to identity-level identification and similarity detection in cyberspace. *ACM Transactions on Information Systems, 26*(2), Article 7.

Acerbi, A., & Stubbersfield, J. M. (2023). Large language models show human-like content biases in transmission chain experiments. *Proceedings of the National Academy of Sciences, 120*(44), e2313790120.

Aher, G., Arriaga, R. I., & Kalai, A. T. (2023). Using large language models to simulate multiple humans and replicate human subject studies. *Proceedings of the 40th International Conference on Machine Learning (ICML 2023)*, PMLR 202.

Aikhenvald, A. Y. (2004). *Evidentiality*. Oxford University Press.

Aikhenvald, A. Y. (Ed.). (2018). *The Oxford handbook of evidentiality*. Oxford University Press.

Alemohammad, S., Casco-Rodriguez, J., Luzi, L., Humayun, A. I., Babaei, H., LeJeune, D., Siahkoohi, A., & Baraniuk, R. G. (2024). Self-consuming generative models go MAD. *Proceedings of the International Conference on Learning Representations (ICLR 2024)*.

Allport, G. W., & Postman, L. (1947). *The psychology of rumor*. Henry Holt.

Argamon, S., Koppel, M., Pennebaker, J. W., & Schler, J. (2009). Automatically profiling the author of an anonymous text. *Communications of the ACM, 52*(2), 119-123.

Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: Using language models to simulate human samples. *Political Analysis, 31*(3), 337-351.

Ashcraft, K. L., Kuhn, T. R., & Cooren, F. (2009). Constitutional amendments: "Materializing" organizational communication. *The Academy of Management Annals, 3*(1), 1-64.

Augenstein, I., Rocktäschel, T., Vlachos, A., & Bontcheva, K. (2016). Stance detection with bidirectional conditional encoding. *Proceedings of EMNLP 2016*, 876-885.

Bai, Y., Kadavath, S., Kundu, S., Askell, A., Kernion, J., Jones, A., Chen, A., Goldie, A., Mirhoseini, A., McKinnon, C., Chen, C., Olsson, C., Olah, C., Hernandez, D., Drain, D., Ganguli, D., Li, D., Tran-Johnson, E., Perez, E., … Kaplan, J. (2022). Constitutional AI: Harmlessness from AI feedback. arXiv:2212.08073.

Bakhtin, M. M. (1981). Discourse in the novel. In M. Holquist (Ed.), *The dialogic imagination: Four essays* (C. Emerson & M. Holquist, Trans., pp. 259-422). University of Texas Press.

Bakhtin, M. M. (1986). The problem of speech genres. In C. Emerson & M. Holquist (Eds.), *Speech genres and other late essays* (V. W. McGee, Trans., pp. 60-102). University of Texas Press.

Baker, W. E., & Faulkner, R. R. (1993). The social organization of conspiracy: Illegal networks in the heavy electrical equipment industry. *American Sociological Review, 58*(6), 837-860.

Bartlett, F. C. (1932). *Remembering: A study in experimental and social psychology*. Cambridge University Press.

Bavelas, A. (1950). Communication patterns in task-oriented groups. *Journal of the Acoustical Society of America, 22*(6), 725-730.

Bazerman, C. (1988). *Shaping written knowledge: The genre and activity of the experimental article in science*. University of Wisconsin Press.

Becker, J., Brackbill, D., & Centola, D. (2017). Network dynamics of social influence in the wisdom of crowds. *Proceedings of the National Academy of Sciences, 114*(26), E5070-E5076.

Becker, J., Porter, E., & Centola, D. (2019). The wisdom of partisan crowds. *Proceedings of the National Academy of Sciences, 116*(22), 10717-10722.

Bergemann, D., & Morris, S. (2019). Information design: A unified perspective. *Journal of Economic Literature, 57*(1), 44-95.

Berkenkotter, C., & Huckin, T. N. (1995). *Genre knowledge in disciplinary communication: Cognition, culture, power*. Lawrence Erlbaum.

Biber, D., & Finegan, E. (1989). Styles of stance in English: Lexical and grammatical marking of evidentiality and affect. *Text, 9*(1), 93-124.

Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024). Synthetic replacements for human survey data? The perils of large language models. *Political Analysis*, advance online publication.

Boelaert, J., Coavoux, S., Ollion, É., Petev, I., & Präg, P. (2025). Machine bias: How do generative language models answer opinion polls? *Sociological Methods & Research*, advance online publication.

Bohnet, B., Tran, V. Q., Verga, P., Aharoni, R., Andor, D., Soares, L. B., Ciaramita, M., Eisenstein, J., Ganchev, K., Herzig, J., Hui, K., Kwiatkowski, T., Ma, J., Ni, J., Saralegui, L. S., Schuster, T., Cohen, W. W., Collins, M., Das, D., … Petrov, S. (2022). Attributed question answering: Evaluation and modeling for attributed large language models. arXiv:2212.08037.

Bond, C. F., & DePaulo, B. M. (2006). Accuracy of deception judgments. *Personality and Social Psychology Review, 10*(3), 214-234.

Bordia, P., & DiFonzo, N. (2004). Problem solving in social interactions on the Internet: Rumor as social cognition. *Social Psychology Quarterly, 67*(1), 33-49.

Bramsen, P., Escobar-Molano, M., Patel, A., & Alonso, R. (2011). Extracting social power relationships from natural language. *Proceedings of ACL 2011*, 773-782.

Brandom, R. B. (1994). *Making it explicit: Reasoning, representing, and discursive commitment*. Harvard University Press.

Brennan, M., Afroz, S., & Greenstadt, R. (2012). Adversarial stylometry: Circumventing authorship recognition to preserve privacy and anonymity. *ACM Transactions on Information and System Security, 15*(3), Article 12.

Brinkmann, L., Baumann, F., Bonnefon, J.-F., Derex, M., Müller, T. F., Nussberger, A.-M., Czaplicka, A., Acerbi, A., Griffiths, T. L., Henrich, J., Leibo, J. Z., McElreath, R., Oudeyer, P.-Y., Stray, J., & Rahwan, I. (2023). Machine culture. *Nature Human Behaviour, 7*, 1855-1868.

Brummans, B. H. J. M., Cooren, F., Robichaud, D., & Taylor, J. R. (2014). Approaches to the communicative constitution of organizations. In L. L. Putnam & D. K. Mumby (Eds.), *The SAGE handbook of organizational communication* (3rd ed., pp. 173-194). SAGE.

Buckner, H. T. (1965). A theory of rumor transmission. *Public Opinion Quarterly, 29*(1), 54-70.

Burge, T. (1993). Content preservation. *The Philosophical Review, 102*(4), 457-488.

Caplow, T. (1947). Rumors in war. *Social Forces, 25*(3), 298-302.

Carson, A. (2017). Facing off and saving face: Covert intervention and escalation management in the Korean War. *International Organization, 71*(1), 103-131.

Cemri, M., Pan, M. Z., Yang, S., Agrawal, L. A., Chopra, B., Tiwari, R., Keutzer, K., Parameswaran, A., Klein, D., Ramchandran, K., Zaharia, M., Gonzalez, J. E., & Stoica, I. (2025). Why do multi-agent LLM systems fail? arXiv:2503.13657.

Centola, D. (2010). The spread of behavior in an online social network experiment. *Science, 329*(5996), 1194-1197.

Centola, D., & Macy, M. (2007). Complex contagions and the weakness of long ties. *American Journal of Sociology, 113*(3), 702-734.

Chafe, W. (1986). Evidentiality in English conversation and academic writing. In W. Chafe & J. Nichols (Eds.), *Evidentiality: The linguistic coding of epistemology* (pp. 261-272). Ablex.

Chafe, W., & Nichols, J. (Eds.). (1986). *Evidentiality: The linguistic coding of epistemology*. Ablex.

Cheng, M., Durmus, E., & Jurafsky, D. (2023). CoMPosT: Characterizing and evaluating caricature in LLM simulations. *Proceedings of EMNLP 2023*.

Cheng, M., Piccardi, T., & Yang, D. (2023). Marked personas: Using natural language prompts to measure stereotypes in language models. *Proceedings of ACL 2023*.

Chuang, Y.-S., Goyal, A., Harlalka, N., Suresh, S., Hawkins, R., Yang, S., Shah, D., Hu, J., & Rogers, T. T. (2024). Simulating opinion dynamics with networks of LLM-based agents. *Findings of NAACL 2024*.

Clark, H. H., & Gerrig, R. J. (1990). Quotations as demonstrations. *Language, 66*(4), 764-805.

Coady, C. A. J. (1992). *Testimony: A philosophical study*. Clarendon Press.

Cooren, F. (2004). Textual agency: How texts do things in organizational settings. *Organization, 11*(3), 373-393.

Cooren, F. (2010). *Action and agency in dialogue: Passion, incarnation and ventriloquism*. John Benjamins.

Crawford, V. P., & Sobel, J. (1982). Strategic information transmission. *Econometrica, 50*(6), 1431-1451.

Daley, D. J., & Kendall, D. G. (1965). Stochastic rumours. *Journal of the Institute of Mathematics and Its Applications, 1*(1), 42-55.

De Marzo, G., Pietronero, L., et al. (2025). Emergent social conventions and collective bias in LLM populations. *Science Advances, 11*(20).

DePaulo, B. M., Lindsay, J. J., Malone, B. E., Muhlenbruck, L., Charlton, K., & Cooper, H. (2003). Cues to deception. *Psychological Bulletin, 129*(1), 74-118.

Diab, M., Levin, L., Mitamura, T., Rambow, O., Prabhakaran, V., & Guo, W. (2009). Committed belief annotation and tagging. *Proceedings of the Third Linguistic Annotation Workshop (LAW III)*, 68-73.

DiFonzo, N., & Bordia, P. (2007a). *Rumor psychology: Social and organizational approaches*. American Psychological Association.

DiFonzo, N., & Bordia, P. (2007b). Rumor, gossip and urban legends. *Diogenes, 54*(1), 19-35.

Du Bois, J. W. (2007). The stance triangle. In R. Englebretson (Ed.), *Stancetaking in discourse: Subjectivity, evaluation, interaction* (pp. 139-182). John Benjamins.

Eckert, P. (2008). Variation and the indexical field. *Journal of Sociolinguistics, 12*(4), 453-476.

Fairclough, N. (1992). *Discourse and social change*. Polity Press.

Faller, M. T. (2002). *Semantics and pragmatics of evidentials in Cuzco Quechua* (Doctoral dissertation, Stanford University).

Farkas, R., Vincze, V., Móra, G., Csirik, J., & Szarvas, G. (2010). The CoNLL-2010 shared task: Learning to detect hedges and their scope in natural language text. *Proceedings of the Fourteenth Conference on Computational Natural Language Learning (CoNLL-2010): Shared Task*, 1-12.

Fricker, E. (1994). Against gullibility. In B. K. Matilal & A. Chakrabarti (Eds.), *Knowing from words* (pp. 125-161). Kluwer.

Friedman, J. A., & Zeckhauser, R. (2012). Assessing uncertainty in intelligence. *Intelligence and National Security, 27*(6), 824-847.

Friedman, J. A., & Zeckhauser, R. (2015). Handling and mishandling estimative probability: Likelihood, confidence, and the search for Bin Laden. *Intelligence and National Security, 30*(1), 77-99.

Gao, T., Yen, H., Yu, J., & Chen, D. (2023). Enabling large language models to generate text with citations. *Proceedings of EMNLP 2023*, 6465-6488.

Gao, Y., Xiong, Y., Gao, X., Jia, K., Pan, J., Bi, Y., Dai, Y., Sun, J., & Wang, H. (2023). Retrieval-augmented generation for large language models: A survey. arXiv:2312.10997.

Goel, S., Anderson, A., Hofman, J., & Watts, D. J. (2016). The structural virality of online diffusion. *Management Science, 62*(1), 180-196.

Goffman, E. (1981). Footing. In *Forms of talk* (pp. 124-159). University of Pennsylvania Press.

Goldberg, S. C. (2007). *Anti-individualism: Mind and language, knowledge and justification*. Cambridge University Press.

Golub, B., & Jackson, M. O. (2010). Naïve learning in social networks and the wisdom of crowds. *American Economic Journal: Microeconomics, 2*(1), 112-149.

Gomez-Rodriguez, M., Leskovec, J., & Krause, A. (2010). Inferring networks of diffusion and influence. *Proceedings of KDD 2010*.

Grice, H. P. (1975). Logic and conversation. In P. Cole & J. L. Morgan (Eds.), *Syntax and semantics, Vol. 3: Speech acts* (pp. 41-58). Academic Press.

Hancock, J. T., Curry, L. E., Goorha, S., & Woodworth, M. (2008). On lying and being lied to: A linguistic analysis of deception in computer-mediated communication. *Discourse Processes, 45*(1), 1-23.

Hans, A., Schwarzschild, A., Cherepanova, V., Kazemi, H., Saha, A., Goldblum, M., Geiping, J., & Goldstein, T. (2024). Spotting LLMs with binoculars: Zero-shot detection of machine-generated text. *Proceedings of ICML 2024*.

Hardwig, J. (1985). Epistemic dependence. *The Journal of Philosophy, 82*(7), 335-349.

Harris, P. L., & Corriveau, K. H. (2011). Young children's selective trust in informants. *Philosophical Transactions of the Royal Society B, 366*(1567), 1179-1187.

Heuer, R. J., Jr. (1999). *Psychology of intelligence analysis*. Center for the Study of Intelligence, CIA.

Heuer, R. J., Jr., & Pherson, R. H. (2019). *Structured analytic techniques for intelligence analysis* (3rd ed.). CQ Press.

Hoes, E., Altay, S., & Bermeo, J. (2023). *Leveraging ChatGPT for efficient fact-checking* (PsyArXiv preprint).

Horton, J. J., Filippas, A., & Manning, B. (2023). *Large language models as simulated economic agents: What can we learn from homo silicus?* (NBER Working Paper No. 31122).

Huang, B., Chen, C., & Shu, K. (2024a). Can large language models identify authorship? *Findings of EMNLP 2024*, 445-460.

Huang, B., Chen, C., & Shu, K. (2024b). Authorship attribution in the era of LLMs: Problems, methodologies, and challenges. arXiv:2408.08946.

Hyland, K. (1998). *Hedging in scientific research articles*. John Benjamins.

Iedema, R. (2001). Resemiotization. *Semiotica, 137*(1/4), 23-39.

Iedema, R. (2003). Multimodality, resemiotization: Extending the analysis of discourse as multi-semiotic practice. *Visual Communication, 2*(1), 29-57.

Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y. J., Madotto, A., & Fung, P. (2023). Survey of hallucination in natural language generation. *ACM Computing Surveys, 55*(12), Article 248.

Johnson, M. K. (2006). Memory and reality. *American Psychologist, 61*(8), 760-771.

Johnson, M. K., Hashtroudi, S., & Lindsay, D. S. (1993). Source monitoring. *Psychological Bulletin, 114*(1), 3-28.

Johnson, M. K., & Raye, C. L. (1981). Reality monitoring. *Psychological Review, 88*(1), 67-85.

Juola, P. (2008). Authorship attribution. *Foundations and Trends in Information Retrieval, 1*(3), 233-334.

Kadane, J. B., & Schum, D. A. (1996). *A probabilistic analysis of the Sacco and Vanzetti evidence*. Wiley.

Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., … Kaplan, J. (2022). Language models (mostly) know what they know. arXiv:2207.05221.

Kamenica, E., & Gentzkow, M. (2011). Bayesian persuasion. *American Economic Review, 101*(6), 2590-2615.

Kashima, Y. (2000). Maintaining cultural stereotypes in the serial reproduction of narratives. *Personality and Social Psychology Bulletin, 26*(5), 594-604.

Kent, S. (1964). Words of estimative probability. *Studies in Intelligence, 8*(4), 49-65.

Kirchenbauer, J., Geiping, J., Wen, Y., Katz, J., Miers, I., & Goldstein, T. (2023). A watermark for large language models. *Proceedings of ICML 2023*.

Knapp, R. H. (1944). A psychology of rumor. *Public Opinion Quarterly, 8*(1), 22-37.

Koenig, M. A., & Harris, P. L. (2005). Preschoolers mistrust ignorant and inaccurate speakers. *Child Development, 76*(6), 1261-1277.

Koppel, M., Schler, J., & Argamon, S. (2009). Computational methods in authorship attribution. *Journal of the American Society for Information Science and Technology, 60*(1), 9-26.

Krebs, V. (2002). Mapping networks of terrorist cells. *Connections, 24*(3), 43-52.

Lackey, J. (2008). *Learning from words: Testimony as a source of knowledge*. Oxford University Press.

Lakoff, G. (1973). Hedges: A study in meaning criteria and the logic of fuzzy concepts. *Journal of Philosophical Logic, 2*, 458-508.

Larooij, M., & Tornberg, P. (2025). Validation is the central challenge for generative social simulation. *AI Review*.

Lazer, D., & Friedman, A. (2007). The network structure of exploration and exploitation. *Administrative Science Quarterly, 52*(4), 667-694.

Leavitt, H. J. (1951). Some effects of certain communication patterns on group performance. *Journal of Abnormal and Social Psychology, 46*(1), 38-50.

Li, J., Sun, S., Wang, K., Liu, T., & Yang, L. (2024). FUSE: Stepwise deception in LLM-driven multi-agent simulation. arXiv:2410.19064 (also EMNLP 2025).

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. *Proceedings of ACL 2022*, 3214-3252.

Lindelauf, R., Borm, P., & Hamers, H. (2009). The influence of secrecy on the communication structure of covert networks. *Social Networks, 31*(2), 126-137.

Lindsay, D. S., & Johnson, M. K. (1989). The eyewitness suggestibility effect and memory for source. *Memory & Cognition, 17*(3), 349-358.

Liu, T., Wang, J., et al. (2025). Simulating rumor spreading in social networks using LLM agents. arXiv:2502.01450.

Liu, X., Yan, Y., Chen, X., Liu, X., & Yang, L. (2024). LLM-driven multi-agent simulation for news diffusion under different network structures. arXiv:2410.13909.

Liu, Y., Iter, D., Xu, Y., Wang, S., Xu, R., & Zhu, C. (2023). G-Eval: NLG evaluation using GPT-4 with better human alignment. *Proceedings of EMNLP 2023*, 2511-2522.

Loftus, E. F., & Palmer, J. C. (1974). Reconstruction of automobile destruction: An example of the interaction between language and memory. *Journal of Verbal Learning and Verbal Behavior, 13*(5), 585-589.

Lokhov, A. Y., Mézard, M., Ohta, H., & Zdeborová, L. (2014). Inferring the origin of an epidemic with a dynamic message-passing algorithm. *Physical Review E, 90*(1), 012801.

Lokhov, A. Y., & Misiakiewicz, T. (2015). Efficient reconstruction of transmission probabilities in a spreading process from partial observations. arXiv:1509.06893.

Lu, X., et al. (2025). Decoding echo chambers: LLM-powered simulations. *COLING 2025*.

MacFarlane, J. (2011). What is assertion? In J. Brown & H. Cappelen (Eds.), *Assertion: New philosophical essays* (pp. 79-96). Oxford University Press.

Mandel, D. R. (2015). Accuracy of intelligence forecasts from the consumer's perspective. *Policy Insights from the Behavioral and Brain Sciences, 2*(1), 111-120.

Mandel, D. R. (2021). Tracking accuracy of strategic intelligence forecasts. *Futures & Foresight Science*.

Mandel, D. R., & Barnes, A. (2014). Accuracy of forecasts in strategic intelligence. *Proceedings of the National Academy of Sciences, 111*(30), 10984-10989.

Manning, B. S., Zhu, K., & Horton, J. J. (2024). *Automated social science: Language models as scientist and subjects* (NBER Working Paper No. 32381).

Mascaro, O., & Sperber, D. (2009). The moral, epistemic, and mindreading components of children's vigilance towards deception. *Cognition, 112*(3), 367-380.

Masip, J., Sporer, S. L., Garrido, E., & Herrero, C. (2005). The detection of deception with the reality monitoring approach: A review of the empirical evidence. *Psychology, Crime & Law, 11*(1), 99-122.

Mason, W., & Watts, D. J. (2012). Collaborative learning in networks. *Proceedings of the National Academy of Sciences, 109*(3), 764-769.

McPhee, R. D., & Zaug, P. (2000). The communicative constitution of organizations: A framework for explanation. *The Electronic Journal of Communication, 10*(1/2).

Mellers, B., Stone, E., Atanasov, P., Rohrbaugh, N., Metz, S. E., Ungar, L., Bishop, M., Horowitz, M., Merkle, E., & Tetlock, P. (2015). The psychology of intelligence analysis: Drivers of prediction accuracy in world politics. *Journal of Experimental Psychology: Applied, 21*(1), 1-14.

Mellers, B., Ungar, L., Baron, J., Ramos, J., Gurcay, B., Fincher, K., Scott, S. E., Moore, D., Atanasov, P., Swift, S. A., Murray, T., Stone, E., & Tetlock, P. E. (2014). Psychological strategies for winning a geopolitical forecasting tournament. *Psychological Science, 25*(5), 1106-1115.

Mercier, H. (2020). *Not born yesterday: The science of who we trust and what we believe*. Princeton University Press.

Mercier, H., & Sperber, D. (2017). *The enigma of reason*. Harvard University Press.

Mesoudi, A., & Whiten, A. (2008). The multiple roles of cultural transmission experiments in understanding human cultural evolution. *Philosophical Transactions of the Royal Society B, 363*(1509), 3489-3501.

Min, S., Krishna, K., Lyu, X., Lewis, M., Yih, W., Koh, P. W., Iyyer, M., Zettlemoyer, L., & Hajishirzi, H. (2023). FActScore: Fine-grained atomic evaluation of factual precision in long-form text generation. *Proceedings of EMNLP 2023*, 12076-12100.

Mitchell, E., Lee, Y., Khazatsky, A., Manning, C. D., & Finn, C. (2023). DetectGPT: Zero-shot machine-generated text detection using probability curvature. *Proceedings of ICML 2023*, 24950-24962.

Mitchell, K. J., & Johnson, M. K. (2000). Source monitoring: Attributing mental experiences. In E. Tulving & F. I. M. Craik (Eds.), *The Oxford handbook of memory* (pp. 179-195). Oxford University Press.

Mitchell, K. J., & Johnson, M. K. (2009). Source monitoring 15 years later: What have we learned from fMRI about the neural mechanisms of source memory? *Psychological Bulletin, 135*(4), 638-677.

Mohammad, S., Kiritchenko, S., Sobhani, P., Zhu, X., & Cherry, C. (2016). SemEval-2016 task 6: Detecting stance in tweets. *Proceedings of SemEval-2016*, 31-41.

Moreno, Y., Nekovee, M., & Pacheco, A. F. (2004). Dynamics of rumor spreading in complex networks. *Physical Review E, 69*(6), 066130.

Mosteller, F., & Wallace, D. L. (1964). *Inference and disputed authorship: The Federalist*. Addison-Wesley.

Mushin, I. (2001). *Evidentiality and epistemological stance: Narrative retelling*. John Benjamins.

Newman, M. L., Pennebaker, J. W., Berry, D. S., & Richards, J. M. (2003). Lying words: Predicting deception from linguistic styles. *Personality and Social Psychology Bulletin, 29*(5), 665-675.

Nguyen, D., Doğruöz, A. S., Rosé, C. P., & de Jong, F. (2016). Computational sociolinguistics: A survey. *Computational Linguistics, 42*(3), 537-593.

Panickssery, A., Bowman, S. R., & Feng, S. (2024). LLM evaluators recognize and favor their own generations. *Advances in Neural Information Processing Systems 37 (NeurIPS 2024)*.

Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). Generative agents: Interactive simulacra of human behavior. *Proceedings of UIST 2023*.

Park, J. S., Popowski, L., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2022). Social simulacra: Creating populated prototypes for social computing systems. *Proceedings of UIST 2022*.

Park, J. S., Zou, C. Q., Shaw, A., Hill, B. M., Cai, C., Morris, M. R., Willer, R., Liang, P., & Bernstein, M. S. (2024). Generative agent simulations of 1,000 people. arXiv:2411.10109.

Peixoto, T. P. (2019). Network reconstruction and community detection from dynamics. *Physical Review Letters, 123*(12), 128301.

Perez, E., Ringer, S., Lukošiūtė, K., Nguyen, K., Chen, E., Heiner, S., Pettit, C., Olsson, C., Kundu, S., Kadavath, S., Jones, A., Chen, A., Mann, B., Israel, B., Seethor, B., McKinnon, C., Olah, C., Yan, D., Amodei, D., … Kaplan, J. (2023). Discovering language model behaviors with model-written evaluations. *Findings of ACL 2023*, 13387-13434.

Perez, J., Léger, C., Ovando-Tellez, M., Foulon, C., Dussauld, J., Oudeyer, P.-Y., & Moulin-Frier, C. (2024). When LLMs play the telephone game: Cumulative changes and attractors in iterated cultural transmissions. arXiv:2407.04503.

Power, M. (1997). *The audit society: Rituals of verification*. Oxford University Press.

Prabhakaran, V., Rambow, O., & Diab, M. (2010). Automatic committed belief tagging. *Proceedings of COLING 2010: Posters*, 1014-1022.

Putnam, L. L., & Nicotera, A. M. (Eds.). (2009). *Building theories of organization: The constitutive role of communication*. Routledge.

Qiu, Y., et al. (2025). Understanding the information propagation effects of communication topologies in LLM-based multi-agent systems. arXiv:2505.23352.

Quelle, D., & Bovet, A. (2024). The perils and promises of fact-checking with large language models. *Frontiers in Artificial Intelligence, 7*, 1341697.

Recanati, F. (2000). *Oratio obliqua, oratio recta: An essay on metarepresentation*. MIT Press.

Rosnow, R. L. (1988). Rumor as communication: A contextualist approach. *Journal of Communication, 38*(1), 12-28.

Rosnow, R. L. (1991). Inside rumor: A personal journey. *American Psychologist, 46*(5), 484-496.

Sadasivan, V. S., Kumar, A., Balasubramanian, S., Wang, W., & Feizi, S. (2023). Can AI-generated text be reliably detected? arXiv:2303.11156.

Salecha, A., Ireland, M. E., Subrahmanian, V. S., et al. (2024). LLMs display human-like social desirability biases. *PNAS Nexus, 3*(12).

Salvi, F., Horta Ribeiro, M., Gallotti, R., & West, R. (2025). On the conversational persuasiveness of GPT-4. *Nature Human Behaviour, 9*.

Schoeneborn, D., Blaschke, S., Cooren, F., McPhee, R. D., Seidl, D., & Taylor, J. R. (2014). The three schools of CCO thinking: Interactive dialogue and systematic comparison. *Management Communication Quarterly, 28*(2), 285-316.

Schum, D. A. (1994). *The evidential foundations of probabilistic reasoning*. Wiley.

Sharma, M., Tong, M., Korbak, T., Duvenaud, D., Askell, A., Bowman, S. R., Cheng, N., Durmus, E., Hatfield-Dodds, Z., Johnston, S. R., Kravec, S., Maxwell, T., McCandlish, S., Ndousse, K., Rausch, O., Schiefer, N., Yan, D., Zhang, M., & Perez, E. (2024). Towards understanding sycophancy in language models. *Proceedings of ICLR 2024*.

Shibutani, T. (1966). *Improvised news: A sociological study of rumor*. Bobbs-Merrill.

Shumailov, I., Shumaylov, Z., Zhao, Y., Papernot, N., Anderson, R., & Gal, Y. (2024). AI models collapse when trained on recursively generated data. *Nature, 631*, 755-759.

Smith, D. E. (2001). Texts and the ontology of organizations and institutions. *Studies in Cultures, Organizations and Societies, 7*(2), 159-198.

Sperber, D., Clément, F., Heintz, C., Mascaro, O., Mercier, H., Origgi, G., & Wilson, D. (2010). Epistemic vigilance. *Mind & Language, 25*(4), 359-393.

Sperber, D., & Wilson, D. (1995). *Relevance: Communication and cognition* (2nd ed.). Blackwell.

Sporer, S. L. (1997). The less travelled road to truth: Verbal cues in deception detection in accounts of fabricated and self-experienced events. *Applied Cognitive Psychology, 11*(5), 373-397.

Sporer, S. L. (2004). Reality monitoring and detection of deception. In P. A. Granhag & L. A. Strömwall (Eds.), *The detection of deception in forensic contexts* (pp. 64-102). Cambridge University Press.

Sporer, S. L. (2016). Deception and cognitive load: Expanding our horizon with a working memory model. *Frontiers in Psychology, 7*, 420.

Squartini, M. (2001). The internal structure of evidentiality in Romance. *Studies in Language, 25*(2), 297-334.

Stamatatos, E. (2009). A survey of modern authorship attribution methods. *Journal of the American Society for Information Science and Technology, 60*(3), 538-556.

Star, S. L., & Strauss, A. (1999). Layers of silence, arenas of voice: The ecology of visible and invisible work. *Computer Supported Cooperative Work, 8*(1-2), 9-30.

Stohl, C., & Stohl, M. (2007). Networks of terror: Theoretical assumptions and pragmatic consequences. *Communication Theory, 17*(2), 93-124.

Stohl, M., & Stohl, C. (2011). Secret agencies: The communicative constitution of a clandestine organization. *Organization Studies, 32*(9), 1197-1215.

Stureborg, R., Alikaniotis, D., & Suhara, Y. (2024). Large language models are inconsistent and biased evaluators. arXiv:2405.01724.

Swales, J. M. (1990). *Genre analysis: English in academic and research settings*. Cambridge University Press.

Tannen, D. (1989). *Talking voices: Repetition, dialogue, and imagery in conversational discourse*. Cambridge University Press.

Tausczik, Y. R., & Pennebaker, J. W. (2010). The psychological meaning of words: LIWC and computerized text analysis methods. *Journal of Language and Social Psychology, 29*(1), 24-54.

Taylor, J. R., & Van Every, E. J. (2000). *The emergent organization: Communication as its site and surface*. Lawrence Erlbaum.

Tecuci, G., Schum, D. A., Marcu, D., & Boicu, M. (2016). *Intelligence analysis as discovery of evidence, hypotheses, and arguments*. Cambridge University Press.

Tetlock, P. E., & Gardner, D. (2015). *Superforecasting: The art and science of prediction*. Crown.

Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. D. (2023). Just ask for calibration: Strategies for eliciting calibrated confidence scores from language models fine-tuned with human feedback. *Proceedings of EMNLP 2023*, 5433-5442.

Tornberg, P., Valeeva, D., Uitermark, J., & Bail, C. (2023). Simulating social media using LLMs. arXiv:2310.05984.

Vandelanotte, L. (2009). *Speech and thought representation in English: A cognitive-functional approach*. Mouton de Gruyter.

Vincze, V., Szarvas, G., Farkas, R., Móra, G., & Csirik, J. (2008). The BioScope corpus: Biomedical texts annotated for uncertainty, negation and their scopes. *BMC Bioinformatics, 9*(Suppl. 11), S9.

Vološinov, V. N. (1973). *Marxism and the philosophy of language* (L. Matejka & I. R. Titunik, Trans.). Harvard University Press. (Original work published 1929)

Vosoughi, S., Roy, D., & Aral, S. (2018). The spread of true and false news online. *Science, 359*(6380), 1146-1151.

Vrij, A. (2008). *Detecting lies and deceit: Pitfalls and opportunities* (2nd ed.). Wiley.

Vrij, A., Granhag, P. A., & Mann, S. (2011). Outsmarting the liars: Toward a cognitive lie detection approach. *Current Directions in Psychological Science, 20*(1), 28-32.

Vrij, A., Mann, S. A., Fisher, R. P., Leal, S., Milne, R., & Bull, R. (2008). Increasing cognitive load to facilitate lie detection: The benefit of recalling an event in reverse order. *Law and Human Behavior, 32*(3), 253-265.

Wang, P., Li, L., Chen, L., Cai, Z., Zhu, D., Lin, B., Cao, Y., Liu, Q., Liu, T., & Sui, Z. (2024). Large language models are not fair evaluators. *Proceedings of ACL 2024*, 9440-9450.

Watts, D. J. (2002). A simple model of global cascades on random networks. *Proceedings of the National Academy of Sciences, 99*(9), 5766-5771.

Wells, G. L., Memon, A., & Penrod, S. D. (2006). Eyewitness evidence: Improving its probative value. *Psychological Science in the Public Interest, 7*(2), 45-75.

Wells, G. L., & Olson, E. A. (2003). Eyewitness testimony. *Annual Review of Psychology, 54*, 277-295.

Willett, T. (1988). A cross-linguistic survey of the grammaticization of evidentiality. *Studies in Language, 12*(1), 51-97.

Williamson, T. (2000). *Knowledge and its limits*. Oxford University Press.

Wilson, D., & Sperber, D. (2012). Explaining irony. In *Meaning and relevance* (pp. 123-145). Cambridge University Press.

Yates, J., & Orlikowski, W. J. (1992). Genres of organizational communication: A structurational approach to studying communication and media. *Academy of Management Review, 17*(2), 299-326.

Yates, J., & Orlikowski, W. J. (2002). Genre systems: Structuring interaction through communicative norms. *Journal of Business Communication, 39*(1), 13-35.

Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y., Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., & Stoica, I. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems 36 (NeurIPS 2023)*.

Zhou, K., Jurafsky, D., & Hashimoto, T. (2023). Navigating the grey area: How expressions of uncertainty and overconfidence affect language models. *Proceedings of EMNLP 2023*, 5506-5524.

Zollman, K. J. S. (2007). The communication structure of epistemic communities. *Philosophy of Science, 74*(5), 574-587.

Zollman, K. J. S. (2013). Network epistemology: Communication in epistemic communities. *Philosophy Compass, 8*(1), 15-27.

Zubiaga, A., Kochkina, E., Liakata, M., Procter, R., Lukasik, M., Bontcheva, K., Cohn, T., & Augenstein, I. (2018). Discourse-aware rumour stance classification in social media using sequential classifiers. *Information Processing & Management, 54*(2), 273-290.

---

## References to Verify

The following entries are likely real but contain bibliographic details that should be confirmed against authoritative sources before formal submission. Authors and rough citation are given so that verification can proceed efficiently.

Carson, A. (2017). The exact title cited above corresponds to Carson's *International Organization* article on the Korean War. Carson also has a book-length treatment of covert signaling (*Secret Wars: Covert Conflict in International Politics*, Princeton University Press, 2018) that may be the more appropriate citation depending on the use. Verify which work is being cited.

Clément, F. (2010). To trust or not to trust? Children's social epistemology. *Review of Philosophy and Psychology, 1*(4). Title and pagination should be confirmed against the Springer record for the journal.

Holt, E., & Clift, R. (Eds.). (2007). *Reporting talk: Reported speech in interaction*. Cambridge University Press. Volume and pagination should be confirmed if a specific chapter is cited.

Murray, S. E. (2014). Varieties of update. *Semantics and Pragmatics, 7*(2), 1-53. Exact pagination should be confirmed.

NATO Standardization Agency. (2016). *Allied joint doctrine for intelligence procedures (AJP-2.1)*. STANAG 2511. NATO. The current edition letter (B or C) and date should be confirmed against the NATO standardization portal before formal citation. The two-axis A-F/1-6 source-credibility grid commonly cited as the "Admiralty Code" is sometimes attributed to British naval intelligence in the early twentieth century with later NATO adoption. The historical attribution should be checked separately from the current STANAG.

Shi, W., Ajith, A., Xia, M., Huang, Y., Liu, D., Blevins, T., Chen, D., & Zettlemoyer, L. (2024). Detecting pretraining data from large language models (Min-K% Prob, WIKIMIA). *Proceedings of ICLR 2024*. Venue placement should be verified against the official ICLR proceedings page.

Uchendu, A., Le, T., Shu, K., & Lee, D. (2023). Neural authorship attribution: Stylometric analysis on large language models. arXiv:2308.07305. Peer-reviewed venue placement is uncertain.

Zhang, Y., Li, Y., Cui, L., Cai, D., Liu, L., Fu, T., Huang, X., Zhao, E., Zhang, Y., Chen, C., Wang, L., Luu, A. T., Bi, W., Shi, F., & Shi, S. (2023). Siren's song in the AI ocean: A survey on hallucination in large language models. *Computational Linguistics* (forthcoming as of last verification). arXiv:2309.01219. Journal version's final volume and page numbers should be confirmed.

The present program's prior Bavelas-style information-mutation studies (referenced generically in §3) should be cited formally once the program's working papers receive stable identifiers.

---

*End of review. Length approximately 11,500 words excluding references.*
