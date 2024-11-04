import argparse
from collections import defaultdict
from vref_utils import Vref
import regex as re
import tqdm


def normalize(text):
    text = text.lower()
    text = re.sub(r"[^a-z ]", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metric",
        choices=["tfidf", "sequence"],
        default="tfidf",
        help="Metric to use for similarity computation",
    )
    parser.add_argument(
        "--books",
        "-b",
        default=None,
        help="List of books (USFM abbreviations) for comparison",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="/tmp/log.txt",
        help="Output file for results",
    )
    parser.add_argument(
        "--scale-factor",
        "-s",
        type=float,
        default=2,
        help="Scale factor for std deviation",
    )

    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    books = [b.strip() for b in args.books.split(",")] if args.books else None

    f = open(args.output, "w")

    def log_print(msg):
        f.write(msg + "\n")

    if args.metric == "tfidf":
        from similarity_metrics.tfidf import compute_similarity
    elif args.metric == "sequence":
        from similarity_metrics.sequence_matcher import compute_similarity
    else:
        raise ValueError(f"Unknown metric {args.metric}")

    print("Using metric:", args.metric)
    paths_as_names = [path.split("/")[-1] for path in args.paths]
    print("Reading files:", paths_as_names)
    vrefs = list(zip(*[Vref(path) for path in args.paths]))

    print("Comparing verses...")
    comparison_count = 0
    accusation_count = defaultdict(int)
    for verse_row in tqdm.tqdm(vrefs):
        if books:
            book = verse_row[0].verse.split(" ")[0]
            if book not in books:
                continue
        score_row = []
        for i, t1 in enumerate(verse_row):
            vref_src = paths_as_names[i]
            text1 = normalize(t1.text)
            if text1 == "" or text1 == "range":
                continue
            for j, t2 in enumerate(verse_row):
                if i >= j:
                    continue
                text2 = normalize(t2.text)
                if text2 == "" or text2 == "range":
                    continue
                vref_tgt = paths_as_names[j]
                try:
                    sim_score = compute_similarity(text1, text2)
                    score_row.append(
                        (
                            {
                                "src": vref_src,
                                "src_ref": t1.verse,
                                "src_text": text1,
                                "tgt": vref_tgt,
                                "tgt_ref": t2.verse,
                                "tgt_text": text2,
                            },
                            sim_score,
                        )
                    )
                except:
                    pass

        # can't compare if there's only one verse
        if len(score_row) < 2:
            continue

        comparison_count += 1
        mean = sum(s for _, s in score_row) / len(score_row)
        std_dev = (sum((s - mean) ** 2 for _, s in score_row) / len(score_row)) ** 0.5

        for i, (details, s) in enumerate(score_row):
            if s - mean > std_dev * args.scale_factor:
                ref = (
                    details["src_ref"]
                    if details["src_ref"] == details["tgt_ref"]
                    else f"{details['src_ref']} <=> {details['tgt_ref']}"
                )
                pair = f"{details["src"]} <=> {details["tgt"]}"
                log_print(f"{ref}: {s} (mean: {mean}, std_dev: {std_dev}) {pair}")
                log_print(f"{details["src"][3:7]}: {details["src_text"]}")
                log_print(f"{details["tgt"][3:7]}: {details["tgt_text"]}")
                for j, t in enumerate(verse_row):
                    log_print(f"\t{paths_as_names[j]}: {t.text}")
                log_print("")
                accusation_count[pair] += 1

    f.close()

    if len(accusation_count) == 0:
        print("No significant overlaps found.")
        return

    accusation_count = sorted(
        accusation_count.items(), key=lambda x: x[1], reverse=True
    )
    for pair, count in accusation_count:
        print(f"{pair}: {count}")

    print(f"Conducted comparisons on {comparison_count} verses.")


if __name__ == "__main__":
    main()
