from tabulate import tabulate
import pandas as pd
import time
import datetime
import pytz
from subprocess import call


class Report:
    def __init__(self, report_name):
        self.report_name = report_name
        self.report_file = f"{self.report_name}.md"
        self._write_header()

    def _write_header(self):
        timestamp = time.time()
        timezone = pytz.timezone("America/Los_Angeles")
        dt = datetime.datetime.fromtimestamp(timestamp, timezone)
        dt_str = dt.strftime("%b %d at %-H:%M")
        with open(self.report_file, "w") as f:
            msg = f"Report generated on {dt_str}."
            print(msg, file=f)

    def write(self, to_write, title=None, cols=None, showindex=False, floatfmt="0.2f"):
        "Add data or text to report."
        self._add_sep()
        if type(to_write) is str:
            with open(self.report_file, "a") as f:
                print(to_write, file=f)
                return

        df = to_write
        if type(df) is not pd.DataFrame:
            df = pd.DataFrame(df).reset_index()
            if cols:
                df.columns = cols
        with open(self.report_file, "a") as f:
            if title is not None:
                f.write("### " + title + "\n\n")
            f.write(tabulate(df, tablefmt="github",
                             showindex=showindex, headers="keys",
                             floatfmt=floatfmt))
        with open(self.report_file, "a") as f:
            f.write("\n")

    def add_fig(self, fig_file, description=""):
        """
        Add figure. Path should be relative to the pandoc compilation path, not
        location of the markdown file.
        """
        self._add_sep()
        fig_text = f"![{description}]({fig_file})"
        with open(self.report_file, "a") as f:
            print(fig_text, file=f)

    def render_pdf(self):
        "Render to PDF using Pandoc."
        pdf_file = f"{self.report_name}.pdf"
        cmd = ["pandoc", self.report_file, "-o", pdf_file, "-t", "html"]
        call(cmd)

    def _add_sep(self):
        "Add separator."
        with open(self.report_file, "a") as f:
            f.write("\n" + 3 * "-" + "\n\n")
