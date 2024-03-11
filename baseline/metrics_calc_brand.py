
import argparse


class BrandIdentificationMetricCalculator():
    def __init__(self) -> None:
        pass

    def calculate_metrics(self, correct, wrong, indeterminate):
        metrics = {}
        total = correct + wrong + indeterminate

        metrics['Precision'] = correct / (correct + wrong)
        metrics['Accuracy'] = correct / total
        metrics['Recall'] = correct / (correct + indeterminate)

        for metric, value in metrics.items():
            print(f"{metric}: {(value * 100):.2f}%")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("correct", help="identified correctly")
    parser.add_argument("wrong", help="identified wrongly")
    parser.add_argument("indeterminate", help="indeterminate")
    args = parser.parse_args()

    metric_calculator = BrandIdentificationMetricCalculator()
    metric_calculator.calculate_metrics(int(args.correct), int(args.wrong), int(args.indeterminate))

