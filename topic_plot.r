source("load_topics.r")
topic_plot <- function (name, topic) {
    pdf(file=paste(name, ".pdf", sep=''), height=4, width=5)
    prob <- topic$prob;
    imi <- topic$imi;
    plot(imi, log(prob))
    dev.off()
}
