# require("mallet")
source("load_topics.r")

state <- load.mallet.state("lda/topic-state.gz")
tabulatedState <- tabulate.state(state)
tabulatedState <- add.groups.to.state(tabulatedState, "lda/metadata.csv")
doc.topics <- tabulatedState$doc.topics
topic.words <- t(tabulatedState$topic.words)

topic.labels <- sapply(1:ncol(doc.topics), function (x) { get.topic.name(tabulatedState, x) })
rownames(topic.words) <- topic.labels
# h <- mallet.topic.hclust(doc.topics, topic.words) -- function is written out below
topic.docs <- t(doc.topics)
topic.docs <- topic.docs/rowSums(topic.docs)
balance <- 0.3
d = balance * dist(topic.words) + (1 - balance) * dist(topic.docs)