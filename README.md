otazkovac
=========

`otazkovac` is a very simple (web|command line) application capable of
generating questions from unstructured[1] Slovak text provided it is fed with
appropriate data. It is intended to be used as a submodule for [Multimedialna
Citanka](https://www.mmcitanka.sk/), a web application thanks to which kids in
the first three grades of Slovak primary schools learn how to read with some
help of a computer. `otazovac` shall be used to help teachers automatically
generate questions from the text their pupils read and thereby test how much
detail from the test were they able to comprehend.

### Question generation

While generation of questions from text might sound like an interesting problem
the amount of academic publications on this topic would suggest otherwise. The
most comprehensive work on this topic currently seems to be Michael Heilman's
dissertation[2] in which many approaches for generating questions from text are
described.

In our case, however, we went for 'easy win' in terms of techniques used for
question generation since the use case of `otazkovac` suggests that the
generated questions do not need to be difficult.

`otazkovac` therefore functions on the following premise: if a sentence starts
with a preposition then this sentence can easily be converted into a sentence
by replacing the prepositional part of it with a preposition (in case of
`otazkovac` either 'kedy' (Slovak for when) or 'kde' (Slovak for where)).

In order for `otazkovac` to find sentences that could potentially be turned
into questions two stages are required: splitting text into sentences and
detecting whether a sentence starts with a preposition. Luckily, both of these
tasks can be performed by MorphoDiTa: Morphological Dictionary and Tagger[3],
provided that it will get the pre-trained model as an input. Thankfully, we
were provided such a model by the Slovak National Corpus[4] under the terms of
the GNU GPLv2 license.

It is important to note that while most of available POS taggers use the Penn
Treebank POS tags[5], Slovak National Corpus uses a specific set of tags[6]
that reflects the nature of Slovak language and provides more information that
might be of use in next stages of processing. For the purpose of our discussion
it shall be noted that preposition tags start with `E`. An example of a tagged
sentence:

```
E---6----------u- - Po
AAis6----x------- - dobrom
SSis6------------ - kúpeli
R---------------- - sa
V-ms---cL-A-d---- - rozlúčil
E---7----------u- - s
SSis7------------ - mesiačikom
O---------------- - a
SSfp7------------ - hviezdičkami
O---------------- - a
V-ms---cL-A-d---- - ľahol
R---------------- - si
V-------I-A-e---- - spať
Z - .
```

As we can see in the example, the first word starts with `E` and is therefore
tagged as a preposition. Note that the next two words share the number 6 in
their tags in the same position as the first word. This is due to the fact that
this position is used for the case of a word and the tagger thinks that these
words are all in the 6th Slovak case which turns out to be Locative. As any
Slovak speaker might also see, these three words can be replaced with 'Kedy',
the full stop with a question mark and we got a sentence that might constitute
a fairly good question:

> **Po dobrom kúpeli** sa rozlúčil s mesiačikom a hviezdičkami a ľahol si spať*.*

then becomes

> **Kedy** sa rozlúčil s mesiačikom a hviezdičkami a ľahol si spať*?*

### Question type detection

Let us consider another example of a sentence with tags for each word:

```
E---6----------u- - V
SSfs6------------ - chate
V--p---aK-A-e---- - sme
R---------------- - sa
V-hp---aL-A-d---- - stretli
E---7----------u- - s
AAms7----x------- - ďalším
SSms7------------ - poľovníkom
Z - .
```

As we can see the first two words in this example are of a similar type as
the words in the first example. However, replacing them with 'Kedy' does not
seem like an option since in Slovak language if the preposition 'v' is followed
by an object and this object itself is not a time reference (such as weekday or
name of a month) this 'prepositional clause' is most probably associated with a
place, not a time. Therefore 'Kde' would be way more appropriate in this case
than 'Kedy'.

Just from these two examples it is obvious that in order for `otazkovac` to
create correct and relevant questions it needs to be able to detect what type
of a question can be generated from a given sentence (if any).

To do so we gathered a dataset of sentences that could possibly be transformed
into questions as described above from all stories available on Multimedialna
Citanka. MorphoDiTa models also provide the lemma along with a tag, we
included this information in the dataset too in order to make the detection
more robust and prone to variation in natural language.

In the end the dataset consists of `695` tagged sentences. Unfortunately, the
premise from above does not hold in general (thanks to variability in natural
language) and there are sentences like 'O zvieratách sa dočítam v encyklopédii
Svet zvierat' in the dataset that do not fall in neither the 'Kde' (marked `P`
for **P**lace in the dataset) nor the 'Kedy' (marked `T` for **T**ime in the
dataset) category. These sentences should be **I**gnored and are therefore
marked `I` in the dataset. The numbers of sentences that belong to respective
categories are as follows:

     I: 24
     T: 240
     P: 431

The dataset is stored in form of a `.csv` file where the first column is the
sentence, the second is the list of lemmatized/tagged words and the third is
one of the types described above. For example:

```
V tíme vyhrávajú buď všetci alebo nikto .	v/E---6----------u- tím/SSis6------------	P
```

#### Feature engineering

A natural choice for features in a scenario like this would be n-grams over the
list of lemmatized words. A slightly better alternative might be to treat POS
tags as words. The motivation behind such a decision might be that it makes
more sense that a sentence of type `P` is more likely to have the preposition
'na' followed by some sort of a noun represented by a tag `SSis6------------`
rather than a specific noun itself. Since the dataset we have is very small
this setup should help us capture more variability in the data.

One last improvement that might help even more would be the addition of
concatenated bigrams from the beginning and the end of the list so that the
list `v/E---6----------u- posledný/NAfs6------------ zákruta/SSfs6------------`
would be represented by a feature vector similar to `v/E---6----------u-
zákruta/SSfs6------------` since the middle word does not change the type.


### Model selection

There are multiple models to choose from when it comes to text classification.
We might use a multinomial Naive Bayes classifier (`NB`) as a baseline, random
forest classifier (`RF`) as an example of a model that tends not to overfit,
and a SVM which is one of the recommended models when it comes to text
classification on small datasets.

All of the models were tested in combination with the features described above
using 10-fold cross validation. The resulting accuracies are provided below:

|             |   NB    |   RF    |  SVM   |
| ----------  | ------- | ------- | ------ |
| 2-3 normal  |  87.36  |  83.90  |  85.90 |
| 2-4 normal  |  88.21  |  85.76  |  86.19 |
| 1-4 specia  |  89.49  |  85.62  |  89.06 |
| 2-4 revers  |  89.49  |  87.06  |  89.06 |
| 2-3 revers  |  89.49  |  88.78  |  90.64 |

The numbers are the degrees of grams which were used (2-3 grams means that
bigrams and trigrams were used), `normal` means setup with just lemmatized
words, `specia` is the setup described in the last paragraph of the section
above and `revers` is the setup in which POS tags are treated as words.

As it turns out our special handcrafted features are essentially the same as
POS tags with 4-grams.

When we train the best model on the whole dataset we get the accuracy of
0.98273381295. This is what the classification report looks like for respective
classes:


    Classification report:
                 precision    recall  f1-score   support

              I       1.00      0.71      0.83        24
              P       0.99      0.99      0.99       431
              T       0.97      1.00      0.98       240

    avg / total       0.98      0.98      0.98       695

And the confusion matrix

|     |  I  |  P  |  T  |
| --- | --- | --- | --- |
|  I  |  17 |   4 |   3 |
|  P  |   0 | 427 |   4 |
|  T  |   0 |   1 | 239 |


It might be interesting to see in which cases did the model failed to predict
the correct class. Here are a few:

> Na konci mesta si našiel lietajúcu motorku a ukradol ju.

Unfortunately in this case (and in many others) the MorphoDiTa model did not
decided that the third word ('mesta') used a different case than the two
before. This is not true but given our premise the model received only the
first two lemmatized words instead of the first three of them which greatly
affected the result.

> Na Havaj sa teším.

In this case the MorphoDiTa model thinks that Havaj is abbreviation or a
special entity of sorts that our premise is not ready for. However, we can also
see that in this case a completely different type of question could be
generated (namely with 'Kam') which shows potential for future improvement.

## Usage

Once we have all the models ready we can actually test `otazkovac` ourselves.

First of all, `otazkovac` needs to be installed by running

    $ python setup.py install

Note that it is written using Python 2.7. The command above will create a new
command `otazkovac` which we can then use on the command line. Assuming that
the MorphoDiTa model and the prediction model generated via `classify.py` are
present in current directory we can test `otazkovac` by running the following
command:

    $ echo "Po dobrom kúpeli sa rozlúčil s mesiačikom a hviezdičkami a ľahol si spať." | otazkovac --morpho-model tagger_model.sk --pipeline pipeline.pkl
    <Question('Kedy sa rozlúčil s mesiačikom a hviezdičkami a ľahol si spať?', answer='Po dobrom kúpeli')>


### Web server (JSON REST API)

`otazkovac` can also be used as a REST API endpoint. In order to turn it on you
need to add the `--server` flag to its command. For example:

    $ otazkovac --morpho-model tagger_model.sk --pipeline pipeline.pkl --server
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

As the debug message suggests, `otazkovac` will respond on
http://127.0.0.1:5000/.

Note that the API endpoint lives at `/questions` and accepts `POST` data in the
field `text`. If you want to see whether the endpoint works you can use the
curl in order to send a `POST` request for example like this:

    $ curl -d 'text=Po dobrom obede pôjdeme spať.' http://127.0.0.1:5000/questions
    {
      "questions": {
        "count": 1,
        "entries": [
          {
            "answer": "Po dobrom obede",
            "question": "Kedy p\u00f4jdeme spa\u0165?"
          }
        ]
      }


If the `"questions"` field is not present in the response object then the
`"error"` field has to be (along with the description of the error):

    $ curl -d 'fero=jano' http://127.0.0.1:5000/questions
    {
      "error": "Missing text parameter"
    }


## Conclusion and Future Work

We present a simple yet quite powerful method for generating simple questions
from unstructured Slovak text. This method incorporates POS tagging as well as
supervised learning of 'question types' for sentences that start with a
preposition.

While this work's focus is on just one possible way of generating questions thanks
to possible sentence transformation[7] this approach might be reusable in other
contexts.

-----------------------------------------------

[1] By which we mean that no special structure of the text is
required. It is expected, however, that the text is grammatically correct and
follows standard stylistic conventions such as using questions marks,
exclamation marks and full stops to determine the end of a sentence.

[2] Heilman, Michael. Automatic factual question generation from text. Diss.
Carnegie Mellon University, 2011.

[3] MorphoDiTa: Morphological Dictionary and Tagger: http://ufal.mff.cuni.cz/morphodita

[4] Slovak National Corpus - Ľ. Štúr Institute of Linguistics, Slovak Academy of Sciences:
http://korpus.juls.savba.sk/index_en.html

[5] http://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html

[6] http://korpus.juls.savba.sk/attachments/morpho_en/tagset-www.pdf

[7] Systems that generate questions from English text (such as Heilman, Michael, and Noah A. Smith. Question generation via overgenerating transformations and ranking. No. CMU-LTI-09-013. CARNEGIE-MELLON UNIV PITTSBURGH PA LANGUAGE TECHNOLOGIES INST, 2009.) usually use Tregex and Tsurgeon expressions that take care of many cases of sentence transformation.
