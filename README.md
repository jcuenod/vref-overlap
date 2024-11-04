# Vref Overlap Detection

This repository detects overlapping sequences in a collection of vref files. It is used to evaluate the uniqueness of a given text relative to a corpus.

## How it works

Imagine we have a few sentences:

1. "The quick brown fox jumps over the lazy dog."
2. "The fast brown fox easily jumps over the lazy dog."
3. "The quick brown jackal leaps over a lazy canine."
4. "The hasty dark wolf shoots past the sleeping dog."

The premise is that, given a similarity function, we can compare the similarity score of multiple texts and create a kind of similarity matrix (the following scores are made up):

|     | 1   | 2   | 3   | 4   |
| --- | --- | --- | --- | --- |
| 1   | 1   | 0.8 | 0.4 | 0.2 |
| 2   | 0.8 | 1   | 0.3 | 0.1 |
| 3   | 0.4 | 0.3 | 1   | 0.1 |
| 4   | 0.2 | 0.1 | 0.1 | 1   |

In this case, we can see that sentences 1 and 2 are very similar, while sentence 4 is quite dissimilar from the rest. This is the basic idea behind the overlap detection algorithm. We compare the similarity of all documents in a collection, triangulating the ones that are "unexpectedly" similar.

We are not evaluating a single sentence but a collection of verses. To aggregate this information across verses, we calculate the mean similarity and the standard deviation for each verse, and we report overlaps when the similarity is more than some threshold above the mean similarity. This means that it is more accurate for larger collections of documents. But the more documents, the longer the processing time.

By default the threshold for reporting overlaps is 2 standard deviations above the mean, but this "scale factor" can be adjusted.

There are two similarity functions, but more can easily be added (feel free to submit a PR!):

1. **TF-IDF**: This method creates a kind of fingerprint for each document based on 1- to 5-grams. This depends on `TfidfVectorizer` from `sklearn.feature_extraction.text`.
2. **Sequence**: This method uses a sliding window to compare sequences of text (irrespective of word boundaries). This depends on `SequenceMatcher` from `difflib`.

## Usage

```bash
$ python main.py --books=GEN,MAT,ROM,HEB ~/vrefs/en-NIV.txt ~/vrefs/en-ESV.txt ~/vrefs/en-CSB.txt ~/vrefs/en-NLT.txt ~/vrefs/en-BSB.txt
Using metric: tfidf
Reading files: ['en-CSB.txt', 'en-NIV.txt', 'en-BSB.txt', 'en-ESV.txt', 'en-NLT.txt']
Comparing verses...
100%|███████████████████████████████████████████████████████████████████████████| 41899/41899 [00:41<00:00, 1012.74it/s]
en-NIV.txt <=> en-BSB.txt: 1098
en-CSB.txt <=> en-BSB.txt: 286
en-CSB.txt <=> en-ESV.txt: 110
en-ESV.txt <=> en-BSB.txt: 100
en-CSB.txt <=> en-NIV.txt: 88
en-NIV.txt <=> en-ESV.txt: 45
en-NLT.txt <=> en-BSB.txt: 29
en-NIV.txt <=> en-NLT.txt: 28
en-CSB.txt <=> en-NLT.txt: 14
en-ESV.txt <=> en-NLT.txt: 4
Conducted comparisons on 3336 verses.
```

You can also use the `--metric=sequence` option to use the sequence method.

```bash
$ python main.py --metric=sequence --books=GEN,MAT,ROM,HEB ~/vrefs/en-CSB.txt ~/vrefs/en-NIV.txt ~/vrefs/en-BSB.txt ~/vrefs/en-ESV.txt ~/vrefs/en-NLT.txt
Using metric: sequence
Reading files: ['en-CSB.txt', 'en-NIV.txt', 'en-BSB.txt', 'en-ESV.txt', 'en-NLT.txt']
Comparing verses...
100%|███████████████████████████████████████████████████████████████████████████| 41899/41899 [00:08<00:00, 5215.25it/s]
en-NIV.txt <=> en-BSB.txt: 370
en-CSB.txt <=> en-BSB.txt: 98
en-CSB.txt <=> en-ESV.txt: 36
en-ESV.txt <=> en-BSB.txt: 23
en-CSB.txt <=> en-NIV.txt: 18
en-NIV.txt <=> en-ESV.txt: 13
en-NLT.txt <=> en-BSB.txt: 13
en-NIV.txt <=> en-NLT.txt: 8
en-CSB.txt <=> en-NLT.txt: 2
Conducted comparisons on 3336 verses.
```

Unsurprisingly, the NLT has the fewest overlaps with other translations.

## Options

- `--metric`: The method to use for comparison. Either `tfidf` or `sequence`. Default is `tfidf`.
- `--books`: A comma-separated list of books to compare. Default is to compare all books.
- `--scale-factor`: The number of standard deviations above the mean similarity to consider an overlap. Default is `2`.
- `--output`: The file to write logs to. Default is `/tmp/output.log`.
