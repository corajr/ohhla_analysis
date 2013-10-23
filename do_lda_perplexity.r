require("tm")
require("topicmodels")

texts <- read.delim("lda/texts.txt", sep="\t", header=F, stringsAsFactors = FALSE, encoding='UTF-8')
rownames(texts) <- texts[,1]

corpus <- Corpus(DataframeSource(texts)) #cbind(texts[,1], texts[,3]

dtm <- DocumentTermMatrix(corpus,
    control = list(stemming = F, stopwords = TRUE, minWordLength = 3, language="english",
    removeNumbers = T))
