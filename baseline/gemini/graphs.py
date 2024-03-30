import argparse
import os
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve, auc
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

class Graph: 
    def __init__(self):
        self.markers = ['o', 's', '^', 'D']
        pass

    def format_title(self, string):
        split_output = string.split('_')
        title = " ".join([split_output[0].capitalize(), split_output[1].capitalize()]) 
        return title
    
    def read_excel(self, path):
        df = pd.read_excel(path)
        df = df.iloc[:1633]
        df = df.iloc[:, :df.columns.get_loc('Is Brand Same?') + 1]

        df['(Gemini) Confidence Score'] = df['(Gemini) Confidence Score'].astype(str)
        df = df[df['(Gemini) Confidence Score'] != "Error Occurred"]
        return df
    
    def get_data_required(self, df, mode):
        if mode == "brand":
            col_label = 'Is Brand Same?'
        else:
            col_label = 'Is Phishing?'
            
        df['Conclusion Binary'] = df[col_label].map({'Yes': 1, 'No': 0, 'Indeterminate': 0}).astype(int)
        df['(Gemini) Confidence Score'] = pd.to_numeric(df['(Gemini) Confidence Score'], errors='coerce')
        df['Normalized Confidence Score'] = df['(Gemini) Confidence Score'] / 10
        df = df.dropna(subset=[col_label, '(Gemini) Confidence Score'])

        true_labels = df['Conclusion Binary']
        confidence_scores = df['Normalized Confidence Score']
        return true_labels, confidence_scores
    

    def plot_precision_recall_curve(self, excel_path, output, mode):
        title = self.format_title(output)
        plt.figure(figsize=(18, 12))

        for excel in excel_path:
            df = self.read_excel(excel)
            true_labels, confidence_scores = self.get_data_required(df, mode)
            precision, recall, thresholds_pr = precision_recall_curve(true_labels, confidence_scores)

            if "ss_html" in excel:
                color = "red"
            elif "ss_" in excel:
                color = "blue"
            elif "html_" in excel:
                color = "green"
            
            if "0_shot" in excel:
                marker = 'o'
            elif "3_shot" in excel:
                marker = '^'
            name = excel.split("/")[-1].split(".xlsx")[0]
            plt.plot(recall, precision, marker=marker, linestyle='-', color=color, label=f'{name}')
        """
        for i, (excel, marker) in enumerate(zip(excel_path, self.markers)):
            df = self.read_excel(excel)
            true_labels, confidence_scores = self.get_data_required(df, mode)
            precision, recall, thresholds_pr = precision_recall_curve(true_labels, confidence_scores)
            plt.plot(recall, precision, marker=marker, linestyle='-', label=f'{i}-shot')
        """
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve for {title}')
        plt.legend()
        plt.grid(True)
        plt.show()
        plt.savefig(os.path.join("baseline", "gemini", f"{output}_PRC.jpg"))
        plt.close()

    def plot_ROC_curve (self, excel_path, output, mode):
        title = self.format_title(output)
        plt.figure(figsize=(16, 12))

        for excel in excel_path:
            df = self.read_excel(excel)
            true_labels, confidence_scores = self.get_data_required(df, mode)
            fpr, tpr, thresholds_roc = roc_curve(true_labels, confidence_scores)
            roc_auc = auc(fpr, tpr)

            if "ss_html" in excel:
                color = "red"
                name = "ss_html"
            elif "ss_" in excel:
                color = "blue"
                name = "ss"
            elif "html_" in excel:
                color = "green"
                name = "html"
            
            if "0_shot" in excel:
                marker = 'o'
                name += " 0 shot"
            elif "3_shot" in excel:
                marker = '^'
                name += " 3 shot"
            
            plt.plot(fpr, tpr, marker=marker, linestyle='-', lw=2, color=color, label=f'{name} (AUC: {roc_auc:.2f})')
            plt.xscale('log')
            fpr_with_no_zero = np.where(fpr == 0, np.min(fpr[np.nonzero(fpr)]), fpr)
            plt.xlim(np.min(fpr_with_no_zero), 1.0)
            plt.ylim([0.0, 1.05])
            plt.xticks([0.001, 0.01, 0.1, 1.25])
            plt.yticks(np.arange(0.0, 1.05, 0.05))
        """
        for i, (excel, marker) in enumerate(zip(excel_path, self.markers)):
            df = self.read_excel(excel)
            true_labels, confidence_scores = self.get_data_required(df, mode)
            fpr, tpr, thresholds_roc = roc_curve(true_labels, confidence_scores)
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, marker=marker, linestyle='-', lw=2, label=f'{i}-shot (AUC: {roc_auc:.2f})')
            plt.xscale('log')
            fpr_with_no_zero = np.where(fpr == 0, np.min(fpr[np.nonzero(fpr)]), fpr)
            plt.xlim(np.min(fpr_with_no_zero), 1.0)
            plt.ylim([0.0, 1.05])
            plt.xticks([0.001, 0.01, 0.1, 1.25])
            plt.yticks(np.arange(0.0, 1.05, 0.05))
        """
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve for {title}')
        plt.legend(loc="lower right")
        plt.grid(True)
        plt.show()
        plt.savefig(os.path.join("baseline", "gemini", f"{output}_ROC.jpg"))
        plt.close()
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Supply the folder names")
    output_name = parser.add_argument("output", help="output file name")
    mode = parser.add_argument("mode", help="brand or phishing")
    args = parser.parse_args()

    ss_html_0_shot = os.path.join("baseline", "gemini", "gemini_responses", "prompt_1_ss_html", "results_0_shot.xlsx")
    ss_html_3_shot = os.path.join("baseline", "gemini", "gemini_responses", "prompt_1_ss_html", "results_3_shot.xlsx")
    ss_0_shot = os.path.join("baseline", "gemini", "gemini_responses", "prompt_1_ss_only", "results_0_shot.xlsx")
    ss_3_shot = os.path.join("baseline", "gemini", "gemini_responses", "prompt_1_ss_only", "results_3_shot.xlsx")
    html_0_shot = os.path.join("baseline", "gemini", "gemini_responses", "prompt_1_html_only", "results_0_shot.xlsx")
    html_3_shot = os.path.join("baseline", "gemini", "gemini_responses", "prompt_1_html_only", "results_3_shot.xlsx")
    excel_paths = [ss_html_0_shot, ss_html_3_shot, ss_0_shot, ss_3_shot, html_0_shot, html_3_shot]
    """
    for i in range(4):
        path = os.path.join("baseline", "gemini", "gemini_responses", "prompt_2", f"{i}-shot", f"results_{i}_shot.xlsx")
        excel_paths.append(path)
    """

    graph_plotter = Graph()
    graph_plotter.plot_precision_recall_curve(excel_paths, args.output, args.mode)
    graph_plotter.plot_ROC_curve(excel_paths, args.output, args.mode)
    