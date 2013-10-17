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
    topic.words <- table(state[state$topic==topic,"word"])
    topic.words <- topic.words / sum(topic.words) #normalize
    sort(topic.words, decreasing=T)[1:n]
}

imi <- function(state, doc.topics, topic, word) {
    entropy(doc.topics[,topic]) - entropy(table(state[state$word == word & state$topic == topic,"doc"]))
}

tabulateState <- function(state) {
    tabulatedState <- state
    tabulatedState$doc.topics <- get.doc.topics(state)
    numTopics <- ncol(tabulatedState$doc.topics)
    tabulatedState$top.words <- lapply(1:numTopics, function (x) { get.top.words(state, x) })
}

top.words.imi <- function(tabulatedState, topic) {
    topic.words <- tabulatedState$top.words[topic][[1]]
    for (word in rownames(topic.words)) { # NOT DONE
        word.imi <- imi(tabulatedState, tabulatedState$doc.topics, topic, word)
    }
    topic.words
}

topic_plot <- function (name, topic) {
    pdf(file=paste(name, ".pdf", sep=''), height=4, width=5)
    prob <- topic$prob;
    imi <- topic$imi;
    plot(imi, log(prob))
    dev.off()
}
