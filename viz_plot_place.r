require(spatstat)
require(RColorBrewer)
require(maps)
library(maptools)
library(ggplot2)
library(MASS)
library(rgeos)
library(grid)
library(gridExtra)


usmap <- map('usa', fill=TRUE, col="transparent", plot=FALSE)
uspoly <- map2SpatialPolygons(usmap, IDs=usmap$names, 
proj4string=CRS("+proj=longlat +datum=wgs84"))
spatstat.options(checkpolygons=FALSE)
usowin <- as.owin.SpatialPolygons(uspoly)
spatstat.options(checkpolygons=TRUE)
theme_map <- function (base_size = 12, base_family = "") {
    theme_gray(base_size = base_size, base_family = base_family) %+replace% 
        theme(
            axis.line=element_blank(),
            axis.text.x=element_blank(),
            axis.text.y=element_blank(),
            axis.ticks=element_blank(),
            axis.ticks.length=unit(0.3, "lines"),
            axis.ticks.margin=unit(0.5, "lines"),
            axis.title.x=element_blank(),
            axis.title.y=element_blank(),
            legend.background=element_rect(fill="white", colour=NA),
            legend.key=element_rect(colour="white"),
            legend.key.size=unit(1.2, "lines"),
            legend.position="right",
            legend.text=element_text(size=rel(0.8)),
            legend.title=element_blank(),#element_text(size=rel(0.8), face="bold", hjust=0),
            panel.background=element_blank(),
            panel.border=element_blank(),
            panel.grid.major=element_blank(),
            panel.grid.minor=element_blank(),
            panel.margin=unit(0, "lines"),
            plot.background=element_blank(),
            plot.margin=unit(c(1, 1, 0.5, 0.5), "lines"),
            plot.title=element_text(size=rel(1.2)),
            strip.background=element_rect(fill="grey90", colour="grey50"),
            strip.text.x=element_text(size=rel(0.8)),
            strip.text.y=element_text(size=rel(0.8), angle=-90) 
        )   
}

########################################################################
## Get kernel density estimates
 
getKde <- function(in_df, N=400, Lims=kde2dRange){
	pts <- as.matrix(in_df[,c('x','y')])
	dens <- kde2d(pts[,1],pts[,2], n=N, lims=Lims)

	dens_df <- data.frame(expand.grid(dens$x, dens$y), z = c(dens$z))
	colnames(dens_df) <- c('x','y','z')
	d1<-SpatialPoints(dens_df,proj4string=CRS("+proj=longlat +datum=wgs84"))
	d2 <- over(d1,uspoly)
 	d1 <- d1[!is.na(d2)] 
	return(as.data.frame(d1))
}
 
plotKde2d <- function(in_df){
	fillCols <- rev(brewer.pal(11,'Spectral'))
	return(
		ggplot() + 
		geom_tile(data = in_df, aes(x=x, y=y, fill=z, group=1)) + 
		scale_fill_gradientn(colours=fillCols) + 
		theme_bw() +
		coord_equal()
	)
}

#Extract Legend 
g_legend<-function(a.gplot){ 
  tmp <- ggplot_gtable(ggplot_build(a.gplot)) 
  leg <- which(sapply(tmp$grobs, function(x) x$name) == "guide-box") 
  legend <- tmp$grobs[[leg]] 
  return(legend)} 



density_map <- function (datapts, name) {
    #datapts <- read.csv(paste(name, ".csv", sep=''))
    test <- data.frame(x=rep(datapts[,1],datapts[,3]),y=rep(datapts[,2],datapts[,3]))
    pts <- as.ppp(test, W=usowin)
    pts <-as.data.frame(pts)
    kde2dRange <- c(apply(pts[,c('x','y')], 2, range))
     
 
    kde2dRange[1] <- kde2dRange[1] -3.0
    kde2dRange[2] <- kde2dRange[2] +3.0
    kde2dRange[3] <- kde2dRange[3] -3.0
    kde2dRange[4] <- kde2dRange[4] +3.0

    dens <- getKde(pts,N=500,Lims=kde2dRange) 
    
    minZ <- (sapply(dens,min)[c('z')])
    maxZ <- (sapply(dens,max)[c('z')])

    fillCols <- rev(brewer.pal(11,'Spectral'))	
    all_states<-map_data("state")
    emap <- ggplot()
    
    emap <- emap+geom_raster(data = dens, aes(x=x, y=y,  fill=z, group=1)) + 
		scale_fill_gradientn(breaks=c(minZ,maxZ), labels=c("Less Occ. ", "More Occ."), colours=fillCols) + 
		coord_equal()
    emap <- emap + geom_path( data=all_states, aes(x=long, y=lat,group = group),colour="white")+theme_map()
    
       legend <- g_legend(emap) 

       #black magic to make ggplot save bar 
       #http://stackoverflow.com/questions/18406991/saving-a-graph-with-ggsave-after-using-ggplot-build-and-ggplot-gtable
       ggsave <- ggplot2::ggsave; body(ggsave) <- body(ggplot2::ggsave)[-2]
       ####

       #grid.draw(legend) 
       ggsave("bar.png", arrangeGrob(legend),height=2,width=1.2)
       emap2 <- emap + theme(legend.position = "none")
       outputname <- paste(name, "_density.pdf", sep='')
       ggsave(outputname, height=4, width=5)
       the.path <- paste(getwd(), "/",outputname , sep = "")
       system(paste("pdfcrop ", the.path, " ", the.path, sep = ""))
       #ggsave(paste(name, "_density.png", sep=''), height=4, width=5)
      
}

# density_map("all_places")
