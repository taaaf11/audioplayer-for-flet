import os
from datetime import timedelta

import flet as ft
from flet import CrossAxisAlignment, MainAxisAlignment, OptionalNumber


class AudioPlayer(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        src_dir: str | None,
        curr_idx: int | None = 0,
        font_family: str | None = None,
        controls_width: OptionalNumber = None,
        controls_vertical_alignment: MainAxisAlignment = MainAxisAlignment.NONE,
        controls_horizontal_alignment: CrossAxisAlignment = CrossAxisAlignment.NONE,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.page_ = page
        self.controls_width = controls_width
        self.font_family = font_family

        self.src_dir = src_dir
        self.curr_idx = curr_idx
        self.src_dir_contents = [
            os.path.join(self.src_dir, folder_content)
            for folder_content in os.listdir(self.src_dir)
            if folder_content.split(".")[-1] == "mp3"
            and not os.path.isdir(os.path.join(self.src_dir, folder_content))
        ]

        self.song_name = ft.Text(
            self._sep_file_ext(os.path.basename(self.src_dir_contents[self.curr_idx]))
        )
        self.seek_bar = ft.ProgressBar(width=self.controls_width)

        # for elapsed time and duration
        self.times_row = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=self.controls_width,
        )

        # play pause next buttons
        self.play_controls = ft.Container(
            ft.Column(
                [
                    ft.Row(
                        [
                            # ft.Text(),  # placeholder, nothing to be placed here
                            ft.IconButton(
                                icon=ft.icons.SKIP_PREVIOUS_SHARP,
                                data="prev",
                                on_click=self.prev_next_music,
                            ),
                            play_pause_btn := ft.IconButton(
                                icon=ft.icons.PLAY_ARROW, on_click=self.play_pause
                            ),
                            ft.IconButton(
                                icon=ft.icons.SKIP_NEXT_SHARP,
                                data="next",
                                on_click=self.prev_next_music,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    ft.Container(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.ADD,
                                    data="inc",
                                    on_click=self.change_vol,
                                    icon_size=18,
                                ),
                                ft.IconButton(
                                    icon=ft.icons.REMOVE,
                                    data="dec",
                                    on_click=self.change_vol,
                                    icon_size=18,
                                ),
                            ],
                            spacing=0,
                            # wrap=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        # border=ft.border.all(2, ft.colors.PINK),
                    ),
                ],
                spacing=0,
                # horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=page.width,
            alignment=ft.alignment.center,
            # border=ft.border.all(2, ft.colors.PURPLE),
            margin=0,
        )

        self.contents = [
            # using container for text alignment center purposes
            ft.Container(
                self.song_name,
                alignment=ft.alignment.center,
                width=controls_width
            ),
            self.seek_bar,
            self.times_row,
            self.play_controls,
        ]

        self.content = ft.Column(
            self.contents,
            alignment=controls_vertical_alignment,
            horizontal_alignment=controls_horizontal_alignment,
        )

        self.audio = ft.Audio(
            src=self.src_dir_contents[self.curr_idx],
            volume=1,
            on_position_changed=self._update_controls,
        )
        self.page_.overlay.append(self.audio)
        self.page_.update()

        self.play_pause_btn = play_pause_btn
        self.playing = False

        self.width = self.controls_width
        # self.border = ft.border.all(2, ft.colors.PURPLE)

        # contents = ft.Column([self.seek_bar])

    def change_vol(self, e):
        if e.control.data == "inc":
            self.audio.volume += 0.1
        elif e.control.data == "dec":
            self.audio.volume -= 0.1
        self.audio.update()

    def prev_next_music(self, e):
        self.audio.pause()
        if e.control.data == "next":
            idx = self.curr_idx + 1
            if idx >= len(self.src_dir_contents):
                idx = len(self.src_dir_contents) - 1
        elif e.control.data == "prev":
            idx = self.curr_idx - 1
            if idx <= 0:
                idx = 0

        self.curr_idx = idx

        self.audio.src = os.path.join(self.src_dir, self.src_dir_contents[idx])
        self.song_name.value = self._sep_file_ext(os.path.basename(self.audio.src))

        self.page_.overlay.append(self.audio)
        self.play_pause_btn.icon = ft.icons.PAUSE
        self.audio.autoplay = True
        self.page_.update()

    def play_pause(self, e):
        if self.playing:
            self.audio.pause()
            self.playing = False
            self.play_pause_btn.icon = ft.icons.PLAY_ARROW
        else:
            self.audio.resume()
            self.playing = True
            self.play_pause_btn.icon = ft.icons.PAUSE
        self.page_.update()

    def _update_controls(self, e):
        curr_time = int(e.data)
        try:
            duration = self.audio.get_duration()
        except:
            return

        self.seek_bar.value = curr_time / duration

        formatted_time_elapsed = self._format_timedelta_str(
            str(timedelta(milliseconds=curr_time))
        )
        formatted_time_duration = self._format_timedelta_str(
            str(timedelta(milliseconds=duration))
        )

        self.times_row.controls = [
            ft.Text(formatted_time_elapsed, font_family=self.font_family),
            ft.Text(formatted_time_duration, font_family=self.font_family),
        ]

        self.page_.update()

    @staticmethod
    def _sep_file_ext(filename: str):
        split_ = filename.split(".")
        if len(split_) > 2:
            return ".".join(split_[:-1])
        else:
            return split_[0]

    def _format_timedelta_str(self, timedelta_str: str):
        full_time = timedelta_str.split(":")
        seconds_field = full_time[-1]
        seconds = seconds_field.split(".")[0]
        try:
            microseconds = seconds_field.split(".")[1]
        except:
            full_time[-1] = seconds
        else:
            full_time[-1] = str(
                round(float(int(seconds) + float("." + str(int(microseconds)))))
            )

        if len(full_time[0]) == 1 and full_time[0] == "0":
            del full_time[0]

        return ":".join(full_time)
