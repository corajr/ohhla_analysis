require("XML")
require("ggplot2")

# pdf("coherences.pdf", width=4,height=5)
# par(mfrow=c(3,2))
# for (i in c(25,50,75,100,125,150)) {
#     doc <- xmlParse(paste(i, "diagnostics-file.txt", sep="/"))
#     coherences <- as.numeric(xpathSApply(doc, "//topic/@coherence"))
#     hist(coherences, main=paste("K=",i, sep=""), xlim=c(-1200,0))
# }
# dev.off()

coherences.df <- data.frame(topics=numeric(0), coherence=numeric(0))
for (i in c(25,50,75,100,125,150)) {
    doc <- xmlParse(paste("lda_compare", i, "diagnostics-file.txt", sep="/"))
    coherences.df <- rbind(coherences.df, data.frame(topics=as.character(i), coherence=as.numeric(xpathSApply(doc, "//topic/@coherence"))))
}

coherence.plot <- ggplot(coherences.df, aes(y=coherence, x=topics)) + geom_boxplot() +
    ylab("Coherence") +
    xlab("# of Topics") +
    coord_flip()

ggsave("coherences.pdf", coherence.plot, width=4, height=3)