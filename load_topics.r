require(ggplot2)

entropy <- function(p) {
    if (min(p) < 0 || sum(p) <= 0)
        return(NA)
    p.norm <- p[p>0]/sum(p)
    -sum(log2(p.norm)*p.norm)
}

# cribbed from benjamin schmidt with modification
# http://journalofdigitalhumanities.org/2-1/code-appendix-for-words-alone-by-benjamin-m-schmidt/

# Load a mallet file, keeping only the doc, typeindex, word, and topic variables
load.mallet.state <- function(fileLocation = "topic-state.gz") {
  read.table(
    file=fileLocation,
    colClasses=c("factor","NULL","NULL","factor","character","factor"),
    comment.char="#",col.names=c("doc","NA","NA2","type","word","topic"))
}

get.doc.topics <- function(state) {
    table(state$doc, state$topic)
}

get.top.words <- function(state, topic, n = 15) {
    topic.words <- table(state[state$topic==topic - 1,"word"])
    topic.words <- topic.words / sum(topic.words) #normalize
    sort(topic.words, decreasing=T)[1:n]
}

imi <- function(tabulatedState, topic, word) {
    state <- tabulatedState$state
    entropy(tabulatedState$doc.topics[,topic]) - entropy(table(state[state$word == word & state$topic == topic - 1,"doc"]))
}

tabulateState <- function(state) {
    tabulatedState <- list(state=state)
    tabulatedState$doc.topics <- get.doc.topics(state)
    numTopics <- ncol(tabulatedState$doc.topics)
    tabulatedState$top.words <- lapply(1:numTopics, function (x) { get.top.words(state, x) })
    tabulatedState
}

top.words.imi <- function(tabulatedState, topic) {
    topic.results <- list()
    topic.words <- tabulatedState$top.words[[topic]]
    topic.results$words <- rownames(topic.words)
    topic.results$prob <- topic.words
    topic.results$imi <- sapply(rownames(topic.words), function (word) {
        imi(tabulatedState, topic, word)
    })
    topic.results
}

topic.mi <- function(state, topic) {
    data <- state[state$topic==topic-1, c("doc", "type")]
    n.k <- nrow(data)
    n.w.k <- table(data$type)
    n.d.k <- table(data$doc)
    n.w.d.k <- table(data) # this is transposed; types are rows and docs are cols

    nonzeros <- which(n.w.d.k!=0, arr.ind=T)
    nwdk <- n.w.d.k[nonzeros]
    terms <- nwdk / n.k
    log.terms <- log((nwdk * n.k) / (n.w.k[nonzeros[,2]] * n.d.k[nonzeros[,1]]))
    sum(terms * log.terms)
}

topic.plot <- function (name, topic.obj) {
    pdf(file=paste(name, ".pdf", sep=''), height=4, width=5)
    df <- data.frame(imi=topic.obj$imi, prob=topic.obj$prob, words=topic.obj$words)
    ggplot(df, aes(x=imi, y=1:nrow(prob), label=words)) +
        geom_point(aes(size=log(prob))) +
        geom_text(size=3, hjust=0)
    dev.off()
}

# e.g.
# state <- load.mallet.state("lda/topic-state.gz")
# tabulatedState <- tabulateState(state)
#
# all.topic.mis <- sapply(1:50, function (x) { topic.mi(state, x)})
#
# topic.obj <- top.words.imi(tabulatedState, 50) 
# topic.plot("topic50label", topic.obj)