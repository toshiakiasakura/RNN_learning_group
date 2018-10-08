library(ggplot2)
library(ggthemes)
library(scales)
library(dplyr)
library(mice)
library(randomForest)

train <- read.csv("~/desktop/train.csv",stringsAsFactors = F)
test <- read.csv("~/desktop/test.csv",stringsAsFactors = F)
full <- bind_rows(train,test)
#データの構造の確認
str(full)
md.pattern(full)

#2. Feature Engineering 
head(full$Name,10)
head(gsub(".*, ","",full$Name),10)
head(gsub("\\..*","",full$Name),10)
head(gsub("(.*, )|(\\..*)","",full$Name),10)
#人の呼称を抜き出す。
full$Title <- gsub("(.*, )|(\\..*)","",full$Name)
#性別によって呼称は変わるので性別によってまとめる。
table(full$Sex,full$Title)
#人数が少ない呼称を全てRare Titleに書き直す。意味が同じ呼称を一つに統合する。
rare_title <- c('Dona', 'Lady', 'the Countess','Capt', 'Col', 'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer')
full$Title[full$Title == "Mlle"]        <- 'Miss' 
full$Title[full$Title == 'Ms']          <- 'Miss'
full$Title[full$Title == 'Mme']         <- 'Mrs' 
full$Title[full$Title %in% rare_title]  <- 'Rare Title'

#変形した後でもう一度集計し直す。
table(full$Sex,full$Title)

#苗字だけを切り出す
full$Surname <- sapply(full$Name,function(x) strsplit(x,"[,.]")[[1]][1])
head(full$Surname,10)

#2.2　家族は沈んだり泳いだり一緒にしたのか？
head(full$SibSp,10)
#家族の大きさを作る。本人の数も忘れないで。
full$Fsize <- full$SibSp + full$Parch +1 
full$Family <- paste(full$Surname,full$Fsize,sep="_")
str(full)

#ggplot2を用いて家族の大きさと生存率の関係性を調べる。
ggplot( full[1:891,], 
  aes(x = Fsize, fill = factor(Survived) ) ) +
  geom_bar(stat='count', position='dodge') +
  scale_x_continuous( breaks= 1:11 ) +
  labs(x = 'Family Size') +
  theme_few()
#家族サイズを離散化する。
full$FsizeD[full$Fsize==1] <- "singleton"
full$FsizeD[full$Fsize >1 & full$Fsize <5] <- "small"
full$FsizeD[full$Fsize >4 ] <- "large"

#モザイクplotで表示する。
table(full$FsizeD, full$Survived)
mosaicplot(table(full$FsizeD, full$Survived), main='Family Size by Survival', shade=TRUE)

#2.3　残りの変数を用いる。
#寝室の番号は使えるのではないか
head(full$Cabin,20)
strsplit(full$Cabin[2],NULL)[[1]]
#デッキの番号だけ取り出してみた。
full$Deck <- factor(sapply(full$Cabin,function(x) strsplit(x,NULL)[[1]][1]))
table(full$Deck)

#3 欠損値の取り扱い
#3.1　繊細な値の補完
#Passengers 62 and 830 はembarkmentが無い
full[c(62,830),"Embarked"]
full$Embarked
embark_fare <- full %>% filter(PassengerId !=62 & PassengerId != 830)
head(embark_fare,10)
ggplot(embark_fare, aes(x = Embarked, y = Fare, fill = factor(Pclass))) +
  geom_boxplot() +
  geom_hline(aes(yintercept=80), 
             colour='red', linetype='dashed', lwd=2) +
  scale_y_continuous(labels=dollar_format()) +
  theme_few()
#このグラフによって欠損値がある乗客の搭乗口がCであるとしても良い事が分かった。

full$Embarked[c(62,830)] <- "C"
full[1044,]
ggplot(full[full$Pclass == '3' & full$Embarked == 'S', ], 
       aes(x = Fare)) +
  geom_density(fill = '#99d6ff', alpha=0.4) + 
  geom_vline(aes(xintercept=median(Fare, na.rm=T)),
             colour='red', linetype='dashed', lwd=1) +
  scale_x_continuous(labels=dollar_format()) +
  theme_few()
#データの補完
full$Fare[1044] <- median(full[full$Pclass ==3 & full$Embarked =="S",]$Fare,na.rm=T)
#3.2年齢の補完を行う。
sum(is.na(full$Age))
#ファクター型の変数をファクター型にする。
factor_vars <- c('PassengerId','Pclass','Sex','Embarked',
                 'Title','Surname','Family','FsizeD')
full[factor_vars] <- lapply(full[factor_vars], function(x) as.factor(x))
#miceはgibbs samplingを行うので、乱数を用いる。
set.seed(129)
#とりあえずmiceを使えばRandam Forestを用いて欠損値が全て埋まる、という印象。
mice_mod <- mice(full[, !names(full) %in% c('PassengerId','Name','Ticket','Cabin','Family','Surname','Survived')], method='rf') 
#アウトプットを全て保存する
mice_output <- complete(mice_mod)
par(mfrow=c(1,2))
hist(full$Age,freq=F,main="Age: Original data",col="darkgreen",ylim=c(0,0.04))
hist(mice_output$Age,freq=F,main="Age: MICE data",col="lightgreen",ylim=c(0,0.04))

#miceを行った結果の形式を確認する。
mice_mod
head(mice_output,20)
#値の代入
full$Age <- mice_output$Age
sum(is.na(full$Age))

#3.3　Feature Engineering: Round2 
#年齢と性別と生存率の相関関係を調べる。性別で区別したのは今までの試行により性別は生存率の大きな因子となっていたからだ。
ggplot(full[1:891,], aes(Age, fill = factor(Survived))) + 
  geom_histogram(bins=30) + 
  facet_grid(.~Sex) + 
  theme_few()
#年齢と生存率は男性の方を見ると若い方が関係していそう。
full$Child[full$Age <18] <- "Child"
full$Child[full$Age >=18] <- "Adult"
table(full$Child,full$Survive)
#tableから子供の方が生き残りやすいことが分かった。
#母親がタイタニックの中で生き残って欲しいと考えるのでMotherの因子も作成する。
full$Mother <- "Not Mother"
full$Mother[full$Sex == "female" & full$Parch > 0 & full$Age >= 18 & full$Title  != "Miss"] <- "Mother"
table(full$Mother,full$Survived)
#母親の方が生き残りやすかった！ 
#今作成した変数をfactorにする。
full$Child <- factor(full$Child)
full$Mother <- factor(full$Mother)

#全ての必要な変数に欠損値が無いことを確認する。
#md.patternはMICEパッケージに入っている。
md.pattern(full)
