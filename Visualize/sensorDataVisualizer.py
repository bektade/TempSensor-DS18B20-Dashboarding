import argparse
import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_EXPORT_DIR = PROJECT_ROOT / 'exports'
DEFAULT_OUTPUT_DIR = Path(
    os.getenv('VISUALIZE_OUTPUT_DIR', PROJECT_ROOT / 'Visualize' / 'output')
)
CSV_GLOB = '*.csv'

TIME_WINDOW_MINUTES = 90
X_TICK_LABEL_MINUTES = (15, 30, 45, 60, 75, 90)
X_GRID_MINUTES = tuple(range(5, TIME_WINDOW_MINUTES + 1, 5))

Y_MIN_C = 20
Y_MAX_C = 70
Y_DTICK_C = 10
Y_MINOR_DTICK_C = 5

Y_MIN_F = 70
Y_MAX_F = 160
Y_DTICK_F = 20
Y_MINOR_DTICK_F = 10

PRESENTATION_WIDTH = 1800
PRESENTATION_HEIGHT = 1100
PRESENTATION_SCALE = 2

BOLD_FONT_FAMILY = 'Arial Black, Helvetica Neue Bold, Liberation Sans Bold, sans-serif'
TICK_COLOR = '#000000'
TITLE_FONT_SIZE = 32
AXIS_TITLE_FONT_SIZE = 24
TICK_FONT_SIZE = 20
LEGEND_FONT_SIZE = 20
TRACE_LINE_WIDTH = 3
TRACE_MARKER_SIZE = 12

VERTICAL_GRID_COLOR = 'rgba(90, 90, 90, 0.5)'  # 50% transparent vertical grids (every 5 min)
HORIZONTAL_GRID_COLOR = 'rgba(90, 90, 90, 0.4)'
HORIZONTAL_GRID_MINOR_COLOR = 'rgba(90, 90, 90, 0.5)'
HORIZONTAL_GRID_WIDTH = 1
HORIZONTAL_GRID_MINOR_WIDTH = 0.5
REFERENCE_BORDER_COLOR = 'rgba(0, 0, 0, 0.5)'


def bold_font(size: int) -> dict[str, int | str]:
    return dict(size=size, family=BOLD_FONT_FAMILY, color=TICK_COLOR)


def plot_timezone() -> ZoneInfo:
    return ZoneInfo(os.getenv('TZ', 'America/Chicago'))


def format_plot_title(session_start: datetime) -> str:
    """Main chart title: test date and time the PNG was generated."""
    tz = plot_timezone()
    generated_at = datetime.now(tz)
    if session_start.tzinfo is None:
        session_date = session_start
    else:
        session_date = session_start.astimezone(tz)
    date_part = session_date.strftime('%m/%d/%Y')
    time_part = generated_at.strftime('%I:%M %p')
    return f'{date_part}  |  {time_part}'


def resolve_latest_csv(export_dir: Path) -> Path:
    candidates = [path for path in export_dir.glob(CSV_GLOB) if path.is_file()]
    if not candidates:
        raise FileNotFoundError(
            f'No CSV in {export_dir}. Start the stack: ./scripts/compose-up.sh'
        )
    return max(candidates, key=lambda path: path.stat().st_mtime)


def load_readings_dataframe(csv_path: Path) -> pd.DataFrame:
    frame = pd.read_csv(csv_path)
    frame['timestamp'] = pd.to_datetime(frame['timestamp'])
    return frame.sort_values('timestamp')


def window_bounds(
    frame: pd.DataFrame,
    window_minutes: int = TIME_WINDOW_MINUTES,
) -> tuple[pd.DataFrame, datetime, datetime]:
    session_start = frame['timestamp'].min().to_pydatetime()
    window_end = session_start + timedelta(minutes=window_minutes)
    mask = (frame['timestamp'] >= session_start) & (frame['timestamp'] <= window_end)
    return frame.loc[mask].copy(), session_start, window_end


def to_plot_time(value: datetime) -> pd.Timestamp:
    return pd.Timestamp(value)


def build_x_tick_marks(session_start: datetime) -> tuple[list[pd.Timestamp], list[str]]:
    tickvals = [
        to_plot_time(session_start + timedelta(minutes=minutes))
        for minutes in X_TICK_LABEL_MINUTES
    ]
    ticktext = [f'{minutes} Min' for minutes in X_TICK_LABEL_MINUTES]
    return tickvals, ticktext


def build_temperature_figure(
    frame: pd.DataFrame,
    session_start: datetime,
    window_end: datetime,
    *,
    title: str,
) -> go.Figure:
    # Two rows, one column: °C on top, °F on bottom, shared x-axis, separate y-axes.
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
    )
    x_tickvals, x_ticktext = build_x_tick_marks(session_start)
    session_start_x = to_plot_time(session_start)
    window_end_x = to_plot_time(window_end)

    palette = px.colors.qualitative.Set2
    sensor_labels = sorted(frame['sensor_label'].unique())

    for index, label in enumerate(sensor_labels):
        subset = frame[frame['sensor_label'] == label]
        color = palette[index % len(palette)]
        line = dict(color=color, width=TRACE_LINE_WIDTH)
        marker = dict(color=color, size=TRACE_MARKER_SIZE)

        fig.add_trace(
            go.Scatter(
                x=subset['timestamp'],
                y=subset['temperature_c'],
                mode='lines+markers',
                name=label,
                line=line,
                marker=marker,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=subset['timestamp'],
                y=subset['temperature_f'],
                mode='lines+markers',
                name=label,
                line=line,
                marker=marker,
                showlegend=False,
            ),
            row=2,
            col=1,
        )

    grid_line = dict(color=VERTICAL_GRID_COLOR, width=1, dash='dash')
    for minutes in X_GRID_MINUTES:
        grid_time = to_plot_time(session_start + timedelta(minutes=minutes))
        if grid_time > window_end_x:
            continue
        for row in (1, 2):
            fig.add_shape(
                type='line',
                x0=grid_time,
                x1=grid_time,
                y0=0,
                y1=1,
                xref='x',
                yref='y domain',
                line=grid_line,
                layer='below',
                row=row,
                col=1,
            )

    border_line = dict(color=REFERENCE_BORDER_COLOR, width=1)
    for row, y_min, y_max in ((1, Y_MIN_C, Y_MAX_C), (2, Y_MIN_F, Y_MAX_F)):
        fig.add_shape(
            type='line',
            x0=session_start_x,
            x1=session_start_x,
            y0=y_min,
            y1=y_max,
            line=border_line,
            row=row,
            col=1,
        )
        fig.add_shape(
            type='line',
            x0=session_start_x,
            x1=window_end_x,
            y0=y_min,
            y1=y_min,
            line=border_line,
            row=row,
            col=1,
        )
        fig.add_shape(
            type='line',
            x0=window_end_x,
            x1=window_end_x,
            y0=y_min,
            y1=y_max,
            line=border_line,
            row=row,
            col=1,
        )
        fig.add_shape(
            type='line',
            x0=session_start_x,
            x1=window_end_x,
            y0=y_max,
            y1=y_max,
            line=border_line,
            row=row,
            col=1,
        )

    axis_title = bold_font(AXIS_TITLE_FONT_SIZE)
    axis_ticks = bold_font(TICK_FONT_SIZE)
    y_axis_ticks = dict(
        tickcolor=TICK_COLOR,
        tickwidth=1,
        ticks='outside',
    )
    y_axis_grid = dict(
        showgrid=True,
        gridwidth=HORIZONTAL_GRID_WIDTH,
        gridcolor=HORIZONTAL_GRID_COLOR,
        griddash='dash',
        zeroline=False,
    )

    fig.update_yaxes(
        range=[Y_MIN_C, Y_MAX_C],
        tick0=Y_MIN_C,
        dtick=Y_DTICK_C,
        ticksuffix='°C',
        title_text='Sauna Temp (°C)',
        title_font=axis_title,
        tickfont=axis_ticks,
        **y_axis_ticks,
        showgrid=True,
        gridwidth=HORIZONTAL_GRID_WIDTH,
        gridcolor=HORIZONTAL_GRID_COLOR,
        griddash='dash',
        zeroline=False,
        minor=dict(
            dtick=Y_MINOR_DTICK_C,
            showgrid=True,
            gridwidth=HORIZONTAL_GRID_MINOR_WIDTH,
            gridcolor=HORIZONTAL_GRID_MINOR_COLOR,
            griddash='dot',
            ticklen=5,
            tickwidth=1,
            tickcolor=TICK_COLOR,
        ),
        row=1,
        col=1,
    )
    fig.update_yaxes(
        range=[Y_MIN_F, Y_MAX_F],
        tick0=Y_MIN_F,
        dtick=Y_DTICK_F,
        ticksuffix='°F',
        title_text='Sauna Temp (°F)',
        title_font=axis_title,
        tickfont=axis_ticks,
        **y_axis_ticks,
        showgrid=True,
        gridwidth=HORIZONTAL_GRID_WIDTH,
        gridcolor=HORIZONTAL_GRID_COLOR,
        griddash='dash',
        zeroline=False,
        minor=dict(
            dtick=Y_MINOR_DTICK_F,
            showgrid=True,
            gridwidth=HORIZONTAL_GRID_MINOR_WIDTH,
            gridcolor=HORIZONTAL_GRID_MINOR_COLOR,
            griddash='dot',
            ticklen=5,
            tickwidth=1,
            tickcolor=TICK_COLOR,
        ),
        row=2,
        col=1,
    )
    x_axis_common = dict(
        range=[session_start_x, window_end_x],
        tickmode='array',
        tickvals=x_tickvals,
        ticktext=x_ticktext,
        showgrid=False,
        title_font=axis_title,
        tickfont=axis_ticks,
    )
    fig.update_xaxes(**x_axis_common, title_text='Time', row=2, col=1)
    fig.update_xaxes(**x_axis_common, showticklabels=False, row=1, col=1)

    fig.update_layout(
        title=dict(
            text=title,
            x=0.02,
            xanchor='left',
            y=0.99,
            yanchor='top',
            font=bold_font(TITLE_FONT_SIZE),
        ),
        width=PRESENTATION_WIDTH,
        height=PRESENTATION_HEIGHT,
        hovermode='x unified',
        hoverlabel=dict(font=bold_font(LEGEND_FONT_SIZE)),
        legend=dict(
            orientation='h',
            yanchor='top',
            y=0.99,
            xanchor='right',
            x=0.98,
            font=bold_font(LEGEND_FONT_SIZE),
            bgcolor='rgba(255, 255, 255, 0.9)',
            borderwidth=0,
        ),
        font=bold_font(TICK_FONT_SIZE),
        paper_bgcolor='#fff',
        plot_bgcolor='#fff',
        margin=dict(l=100, r=48, t=130, b=96),
    )

    return fig


class SensorDataVisualizer:
    def __init__(
        self,
        csv_path: Path | None = None,
        export_dir: Path | None = None,
        time_window_minutes: int = TIME_WINDOW_MINUTES,
    ) -> None:
        self.export_dir = Path(export_dir or DEFAULT_EXPORT_DIR)
        self.csv_path = Path(csv_path) if csv_path else resolve_latest_csv(self.export_dir)
        self.time_window_minutes = time_window_minutes
        self.frame = pd.DataFrame()
        self.session_start: datetime | None = None
        self.window_end: datetime | None = None

    def load_data(self) -> None:
        loaded = load_readings_dataframe(self.csv_path)
        if loaded.empty:
            raise RuntimeError(f'No sensor rows in {self.csv_path}.')
        self.frame, self.session_start, self.window_end = window_bounds(
            loaded,
            window_minutes=self.time_window_minutes,
        )
        if self.frame.empty:
            raise RuntimeError(
                f'No sensor data in the first {self.time_window_minutes} minutes of {self.csv_path}.'
            )

    def build_figure(self) -> go.Figure:
        assert self.session_start is not None and self.window_end is not None
        return build_temperature_figure(
            self.frame,
            self.session_start,
            self.window_end,
            title=format_plot_title(self.session_start),
        )

    def plot(
        self,
        output_path: Path | None = None,
        *,
        presentation: bool = False,
    ) -> Path | None:
        figure = self.build_figure()
        if output_path is None:
            figure.show()
            return None

        saved = Path(output_path)
        saved.parent.mkdir(parents=True, exist_ok=True)
        scale = PRESENTATION_SCALE if presentation else 1
        try:
            figure.write_image(str(saved), scale=scale)
            print(f'Saved plot: {saved}', flush=True)
        except Exception as error:
            html_path = saved.with_suffix('.html')
            figure.write_html(str(html_path), include_plotlyjs='cdn')
            raise RuntimeError(
                f'PNG export failed ({error}). Interactive HTML saved: {html_path}'
            ) from error
        return saved


def presentation_png_path(csv_path: Path, output_dir: Path | None = None) -> Path:
    directory = Path(output_dir or DEFAULT_OUTPUT_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f'{csv_path.name.removesuffix(".csv")}.png'


def plot_latest_presentation(
    export_dir: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    root = Path(export_dir or os.getenv('CSV_DIR', DEFAULT_EXPORT_DIR))
    csv_path = resolve_latest_csv(root)
    visualizer = SensorDataVisualizer(csv_path=csv_path, export_dir=root)
    visualizer.load_data()
    png_path = presentation_png_path(csv_path, output_dir)
    visualizer.plot(output_path=png_path, presentation=True)
    return png_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Plot DS18B20 readings (°C and °F) from the latest exports CSV.'
    )
    parser.add_argument(
        '--export-dir',
        type=Path,
        default=Path(os.getenv('CSV_DIR', DEFAULT_EXPORT_DIR)),
    )
    parser.add_argument('--csv', type=Path)
    parser.add_argument(
        '--minutes',
        type=int,
        default=TIME_WINDOW_MINUTES,
        help=f'Time window in minutes (default: {TIME_WINDOW_MINUTES})',
    )
    parser.add_argument('-o', '--output', type=Path)
    parser.add_argument('--presentation', action='store_true')
    parser.add_argument('--output-auto', action='store_true')
    args = parser.parse_args()

    visualizer = SensorDataVisualizer(
        csv_path=args.csv,
        export_dir=args.export_dir,
        time_window_minutes=args.minutes,
    )
    print(f'Using CSV: {visualizer.csv_path}', flush=True)
    visualizer.load_data()

    output = args.output
    if args.output_auto:
        output = presentation_png_path(
            visualizer.csv_path,
            Path(os.getenv('VISUALIZE_OUTPUT_DIR', DEFAULT_OUTPUT_DIR)),
        )

    presentation = args.presentation or args.output_auto
    if output is None:
        visualizer.plot(presentation=False)
    else:
        visualizer.plot(output_path=output, presentation=presentation)


if __name__ == '__main__':
    main()
