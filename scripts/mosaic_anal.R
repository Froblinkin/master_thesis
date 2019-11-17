# Generate mosaic plots 

library(vcd)
library(colorspace)

# Interval target variable 
tab<-read.table("data/combined_count2.csv",sep=",",header = FALSE)
tab<-as.table(as.matrix(tab))
colnames(tab)<-c("1-4","5-8","9-12","13-16","17-20","21+")
rownames(tab)<-rev(c("1","2-5","6-10","11-20","21-40","41-60","61-100"))
mosaic(tab,shade=T,labeling=labeling_values,ylab="weeks interval",xlab="peak interval")
mosaicplot(tab,color=rainbow_hcl(6),ylab="Weeks interval",xlab="Peak interval",main="",las=1)

# Alignment target variable through time 
tab<-read.table("data/time_align.csv",sep=",",header = FALSE)
tab<-as.table(as.matrix(tab),cex=0.3)
rownames(tab)<-seq(11)
colnames(tab)<-seq(40)
mosaicplot(tab,color=rainbow_hcl(40),ylab="Alignment class label",xlab="Time block (5 year intervals)",main="",las=1,cex=0.5)

# Interval target variable through time 
tab<-read.table("data/time_interval.csv",sep=",",header = FALSE)
tab<-as.table(as.matrix(tab),cex=0.3)
rownames(tab)<-seq(11)
colnames(tab)<-seq(42)
mosaicplot(tab,color=rainbow_hcl(42),ylab="Interval class label",xlab="Time block (5 year intervals)",main="",las=1,cex=0.5)


