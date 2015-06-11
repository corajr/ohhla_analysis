topic.plot <- function (name, topic.obj, title, xlab="IMI(w,G|k)") {
    df <- data.frame(imi=topic.obj$imi, prob=topic.obj$prob, words=topic.obj$words)
    filename <- paste(name, ".pdf", sep='')
    this.plot <- ggplot(df, aes(x=imi, y=1:length(prob), label=words)) +
        geom_point(aes(size=log(prob)), show_guide=FALSE) + scale_area(range=c(1,3)) +
        geom_text(size=4, hjust=-0.3) +
        theme_bw() +
        ggtitle(title) +
        xlab(xlab) +
        xlim(0, 1.0) +
        ylab("Rank") +
        scale_y_reverse()
    ggsave(filename, this.plot, width=4, height=3)
}
top.words.imi <- function(tabulatedState, topic, group="year") {
    topic.results <- list()
    topic.words <- tabulatedState$top.words[[topic]]
    topic.results$words <- attr(topic.words, "names")
    topic.results$prob <- topic.words
    topic.results$imi <- sapply(topic.results$words , function (word) {
        imi.group(tabulatedState, topic, word, group)
    })
    topic.results
}


plot.hood <- function(tabulatedState) {
    categories <- list(c("artist","Artist"), c("place","Place"), c("year", "Year"))
    for (cat.tuple in categories) {
        mygroup <- cat.tuple[1]
        mytitle <- cat.tuple[2]
        topic.obj <- top.words.imi(tabulatedState, 40, mygroup)
        topic.plot(paste("hood", mygroup, sep="."), topic.obj, mytitle)
    }
}
plot.hood(tabulatedState)