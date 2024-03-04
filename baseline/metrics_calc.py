
import argparse


class MetricCalculator():
    def __init__(self) -> None:
        pass

    def calculate_metrics(self, tp, tn, fp, fn):
        metrics = {}
        metrics['TPR'] = tp / (tp + fn) if (tp + fn) else 0
        metrics['TNR'] = tn / (tn + fp) if (tn + fp) else 0
        metrics['FPR'] = fp / (fp + tn) if (fp + tn) else 0
        metrics['FNR'] = fn / (tp + fn) if (tp + fn) else 0

        metrics['Precision'] = tp / (tp + fp) if (tp + fp) else 0
        metrics['Accuracy'] = (tp + tn) / (tp + tn + fp + fn) if  (tp + tn + fp + fn) else 0
        metrics['Recall'] = tp / (tp + fn) if (tp + fn) else 0

        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    parser.add_argument("tp", help="true positive")
    parser.add_argument("tn", help="true negative")
    parser.add_argument("fp", help="false positive")
    parser.add_argument("fn", help="false negative")
    args = parser.parse_args()

    metric_calculator = MetricCalculator()
    metric_calculator.calculate_metrics(args.tp, args.tn, args.fp, args.fn)

    