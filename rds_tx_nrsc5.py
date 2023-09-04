#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Rds Tx Nrsc5
# GNU Radio version: v3.10.5.1-37-ga5a387bf

from packaging.version import Version as StrictVersion
from PyQt5 import Qt
from gnuradio import qtgui
from fractions import Fraction
from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import network
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import math
import nrsc5
import osmosdr
import time
import paint
import rds
import sip



class rds_tx_nrsc5(gr.top_block, Qt.QWidget):

    def __init__(self, ana_delay=4.5, bb_gain=(-4), dc_offset=0, digi_delay=0, tx_rate=2000000):
        gr.top_block.__init__(self, "Rds Tx Nrsc5", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Rds Tx Nrsc5")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "rds_tx_nrsc5")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Parameters
        ##################################################
        self.ana_delay = ana_delay
        self.bb_gain = bb_gain
        self.dc_offset = dc_offset
        self.digi_delay = digi_delay
        self.tx_rate = tx_rate

        ##################################################
        # Variables
        ##################################################
        self.rds_gain = rds_gain = 0.05
        self.pilot_gain = pilot_gain = 0.1
        self.usrp_rate = usrp_rate = 500e3
        self.input_gain = input_gain = (0.5-rds_gain/2-pilot_gain/2)*1.95
        self.audio_rate = audio_rate = 44100
        self.threads = threads = 1
        self.sum_gain = sum_gain = 1
        self.rds_taps = rds_taps = firdes.band_pass(1.0, usrp_rate, 55e3, 59e3, 300, window.WIN_BLACKMAN, 6.76)
        self.pilot_taps = pilot_taps = firdes.band_pass(1/pilot_gain*2, usrp_rate, 37980, 38020, 1000, window.WIN_HAMMING, 6.76)
        self.p2rate = p2rate = 6000
        self.p1rate = p1rate = 16000
        self.nrsc_gain = nrsc_gain = 0.0065
        self.maxpsdbuf = maxpsdbuf = 128
        self.lpf_taps = lpf_taps = firdes.low_pass(1.0, tx_rate, 105e3,10e3, window.WIN_HAMMING, 6.76)
        self.freq = freq = 90.1e6
        self.fm_max_dev = fm_max_dev = 75e3
        self.emphasis_clip_taps = emphasis_clip_taps = firdes.low_pass(input_gain, usrp_rate, 15e3,1e3, window.WIN_HAMMING, 6.76)
        self.diff_gain = diff_gain = 1.25
        self.decim = decim = 2**15
        self.dc_corr = dc_corr = dc_offset
        self.clip_level = clip_level = 0.5
        self.bpf_taps_sca = bpf_taps_sca = firdes.band_pass(1.0, usrp_rate, 67e3, 67e3+5e3, 1000, window.WIN_HAMMING, 6.76)
        self.bbrail = bbrail = (1-pilot_gain-rds_gain)
        self.bb_clip_taps = bb_clip_taps = firdes.low_pass(1, usrp_rate, 53e3,2e3, window.WIN_HAMMING, 6.76)
        self.audio_gain = audio_gain = .44
        self.ana_gain = ana_gain = 0.45
        self.afrail = afrail = 1
        self.a_lpf_taps_sca = a_lpf_taps_sca = firdes.low_pass(0.5, audio_rate, 5e3,1e3, window.WIN_HAMMING, 6.76)
        self.a_lpf_taps = a_lpf_taps = firdes.low_pass(0.5, audio_rate, 16e3,1e3, window.WIN_HAMMING, 6.76)
        self.BB_gain = BB_gain = bb_gain

        ##################################################
        # Blocks
        ##################################################

        self._sum_gain_range = Range(0, 2, 0.001, 1, 200)
        self._sum_gain_win = RangeWidget(self._sum_gain_range, self.set_sum_gain, "SUM Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._sum_gain_win)
        self._nrsc_gain_range = Range(0, 0.1, 0.0001, 0.0065, 200)
        self._nrsc_gain_win = RangeWidget(self._nrsc_gain_range, self.set_nrsc_gain, "Digi Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._nrsc_gain_win)
        self._diff_gain_range = Range(0, 30, 0.001, 1.25, 200)
        self._diff_gain_win = RangeWidget(self._diff_gain_range, self.set_diff_gain, "DIFF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._diff_gain_win)
        self._dc_corr_range = Range(-0.1, 0.1, 0.00001, dc_offset, 200)
        self._dc_corr_win = RangeWidget(self._dc_corr_range, self.set_dc_corr, "DC Correction", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._dc_corr_win)
        self._audio_gain_range = Range(0, 2, 0.001, .44, 200)
        self._audio_gain_win = RangeWidget(self._audio_gain_range, self.set_audio_gain, "Audio Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._audio_gain_win)
        self._ana_gain_range = Range(0, 1, 0.001, 0.45, 200)
        self._ana_gain_win = RangeWidget(self._ana_gain_range, self.set_ana_gain, "Analog Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._ana_gain_win)
        self._BB_gain_range = Range(-10, 10, 0.1, bb_gain, 200)
        self._BB_gain_win = RangeWidget(self._BB_gain_range, self.set_BB_gain, "Baseband Gain (dB)", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._BB_gain_win)
        self.zeromq_sub_source_0_0_0 = zeromq.sub_source(gr.sizeof_float, 2, 'tcp://localhost:2000', 3000, False, (-1), '')
        self.zeromq_sub_source_0_0 = zeromq.sub_source(gr.sizeof_float, 2, 'tcp://localhost:2000', 3000, False, (-1), '')
        self.root_raised_cosine_filter_0 = filter.interp_fir_filter_fff(
            160,
            firdes.root_raised_cosine(
                111,
                380e3,
                2375,
                1,
                (160*11)))
        self.root_raised_cosine_filter_0.set_max_output_buffer(4096)
        self.rds_encoder_0 = rds.encoder(1, 15, True, 'GRCon-FM', freq,
        			False, False, 13, 0,
        			147, '1. flag{AbolitionOfMan}')

        self.rds_encoder_0.set_max_output_buffer(maxpsdbuf)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=16,
                decimation=1,
                taps=[],
                fractional_bw=0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_f(
            32768, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            usrp_rate, #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)


        self.qtgui_waterfall_sink_x_0.set_plot_pos_half(not False)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-140, 0)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_layout.addWidget(self._qtgui_waterfall_sink_x_0_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
            1024, #size
            usrp_rate, #samp_rate
            "baseband", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_win)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            1024, #size
            usrp_rate, #samp_rate
            "Audio", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(1/10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['SUM', 'DIFF', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            tx_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/(1/10))
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.qtgui_number_sink_0_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            3,
            None # parent
        )
        self.qtgui_number_sink_0_0.set_update_time(1/10)
        self.qtgui_number_sink_0_0.set_title("Power")

        labels = ['PAPR', 'Max Power', 'Avg. Power', '', '',
            '', '', '', '', '']
        units = ['dB', 'dB', 'dB', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(3):
            self.qtgui_number_sink_0_0.set_min(i, 0)
            self.qtgui_number_sink_0_0.set_max(i, 40)
            self.qtgui_number_sink_0_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0.enable_autoscale(False)
        self._qtgui_number_sink_0_0_win = sip.wrapinstance(self.qtgui_number_sink_0_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_number_sink_0_0_win)
        self.qtgui_number_sink_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_HORIZ,
            1,
            None # parent
        )
        self.qtgui_number_sink_0.set_update_time(1/30)
        self.qtgui_number_sink_0.set_title("")

        labels = ['Max Deviation', 'Max Deviation Mod', '', '', '',
            '', '', '', '', '']
        units = ['kHz', 'kHz', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [fm_max_dev, fm_max_dev, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0.set_min(i, 0)
            self.qtgui_number_sink_0.set_max(i, fm_max_dev*1.1)
            self.qtgui_number_sink_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0.set_label(i, labels[i])
            self.qtgui_number_sink_0.set_unit(i, units[i])
            self.qtgui_number_sink_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0.enable_autoscale(False)
        self._qtgui_number_sink_0_win = sip.wrapinstance(self.qtgui_number_sink_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_number_sink_0_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_f(
            16384, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            usrp_rate, #bw
            "TX BB", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_0.set_plot_pos_half(not False)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.paint_paint_bc_0 = paint.paint_bc(288, 1, paint.EQUALIZATION_OFF, paint.INTERNAL, 1)
        self.paint_image_source_0 = paint.image_source('flag16.png', 0, 1, 0, 0, 1)
        self.osmosdr_sink_0 = osmosdr.sink(
            args="numchan=" + str(1) + " " + ""
        )
        self.osmosdr_sink_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.osmosdr_sink_0.set_sample_rate(tx_rate)
        self.osmosdr_sink_0.set_center_freq(freq, 0)
        self.osmosdr_sink_0.set_freq_corr(0, 0)
        self.osmosdr_sink_0.set_gain(14, 0)
        self.osmosdr_sink_0.set_if_gain(40, 0)
        self.osmosdr_sink_0.set_bb_gain(20, 0)
        self.osmosdr_sink_0.set_antenna('', 0)
        self.osmosdr_sink_0.set_bandwidth(0, 0)
        self.nrsc5_sis_encoder_0 = nrsc5.sis_encoder(mode=nrsc5.pids_mode.FM, short_name='GRCN', slogan='AES:kjhASty34e987o76w6ta&B6g ', message='3. flag{GodsOfTheCopybookHeadings}', program_types=[nrsc5.program_type.CLASSICAL, nrsc5.program_type.TALK, nrsc5.program_type.NEWS, nrsc5.program_type.NEWS, nrsc5.program_type.NEWS, nrsc5.program_type.NEWS, nrsc5.program_type.NEWS, nrsc5.program_type.NEWS], latitude=47, longitude=(-105), altitude=2000, country_code='US', fcc_facility_id=4213)
        self.nrsc5_psd_encoder_0_1_1_0 = nrsc5.psd_encoder(4, 'Four', 'DK1Q}', 128)
        self.nrsc5_psd_encoder_0_1_1_0.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_psd_encoder_0_1_1 = nrsc5.psd_encoder(3, 'Three', '=uxVhova', 128)
        self.nrsc5_psd_encoder_0_1_1.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_psd_encoder_0_1_0 = nrsc5.psd_encoder(2, 'Two', 'ag{watch?v', 128)
        self.nrsc5_psd_encoder_0_1_0.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_psd_encoder_0_1 = nrsc5.psd_encoder(1, 'One', '4.fl', 128)
        self.nrsc5_psd_encoder_0_1.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_psd_encoder_0_0_0_0 = nrsc5.psd_encoder(7, 'flag{Nyquist}', '7.', 0)
        self.nrsc5_psd_encoder_0_0_0_0.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_psd_encoder_0_0_0 = nrsc5.psd_encoder(6, 'N', '69', 0)
        self.nrsc5_psd_encoder_0_0_0.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_psd_encoder_0_0 = nrsc5.psd_encoder(5, '7F4DA1B2C30100', '4A63C7DEA2667B3222CDD6A1746702', 128)
        self.nrsc5_psd_encoder_0_0.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_psd_encoder_0 = nrsc5.psd_encoder(0, 'Various', 'VladFM', 128)
        self.nrsc5_psd_encoder_0.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_lot_encoder_0_3 = nrsc5.lot_encoder('HD6_1.png', 5, 0x100B)
        self.nrsc5_lot_encoder_0_2_0_0_0 = nrsc5.lot_encoder('uio.png', 4, 0x1009)
        self.nrsc5_lot_encoder_0_2_0_0 = nrsc5.lot_encoder('zxc.png', 3, 0x1007)
        self.nrsc5_lot_encoder_0_2_0 = nrsc5.lot_encoder('dfg.png', 2, 0x1005)
        self.nrsc5_lot_encoder_0_2 = nrsc5.lot_encoder('bnm.png', 1, 0x1003)
        self.nrsc5_lot_encoder_0_0_0_0 = nrsc5.lot_encoder('HD8a.png', 7, 0x100F)
        self.nrsc5_lot_encoder_0_0 = nrsc5.lot_encoder('HD7.png', 6, 0x100D)
        self.nrsc5_lot_encoder_0 = nrsc5.lot_encoder('HD1.jpg', 0, 0x1001)
        self.nrsc5_l2_encoder_0_0 = nrsc5.l2_encoder(2, 6, 4608, 10)
        self.nrsc5_l2_encoder_0_0.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_l2_encoder_0 = nrsc5.l2_encoder(6, 0, 146176, 1000)
        self.nrsc5_l2_encoder_0.set_max_output_buffer(maxpsdbuf)
        self.nrsc5_l1_fm_encoder_mp3_0 = nrsc5.l1_fm_encoder(3)
        self.nrsc5_hdc_encoder_0_1_0_0_0 = nrsc5.hdc_encoder(1, p2rate)
        self.nrsc5_hdc_encoder_0_1_0_0 = nrsc5.hdc_encoder(1, p1rate)
        self.nrsc5_hdc_encoder_0_1_0 = nrsc5.hdc_encoder(1, p1rate)
        self.nrsc5_hdc_encoder_0_1 = nrsc5.hdc_encoder(1, p1rate)
        self.nrsc5_hdc_encoder_0_0_1 = nrsc5.hdc_encoder(1, p2rate)
        self.nrsc5_hdc_encoder_0_0_0 = nrsc5.hdc_encoder(1, p2rate)
        self.nrsc5_hdc_encoder_0_0 = nrsc5.hdc_encoder(1, p1rate)
        self.nrsc5_hdc_encoder_0 = nrsc5.hdc_encoder(1, p1rate)
        self.network_socket_pdu_0_1_1 = network.socket_pdu('TCP_SERVER', '0.0.0.0', '52003', 10000, False)
        self.network_socket_pdu_0_1_0_0_0 = network.socket_pdu('TCP_SERVER', '0.0.0.0', '52004', 10000, False)
        self.network_socket_pdu_0_1 = network.socket_pdu('TCP_SERVER', '0.0.0.0', '52002', 10000, False)
        self.network_socket_pdu_0 = network.socket_pdu('TCP_SERVER', '', '52001', 10000, False)
        self.mmse_resampler_xx_1 = filter.mmse_resampler_ff(0, 1.5)
        self.mmse_resampler_xx_0_0_3 = filter.mmse_resampler_ff(0, (audio_rate/usrp_rate))
        self.mmse_resampler_xx_0_0_2 = filter.mmse_resampler_ff(0, (380e3/usrp_rate))
        self.mmse_resampler_xx_0_0_2.set_max_output_buffer(4096)
        self.mmse_resampler_xx_0_0_1 = filter.mmse_resampler_cc(0, (usrp_rate/tx_rate))
        self.mmse_resampler_xx_0_0_0 = filter.mmse_resampler_ff(0, (audio_rate/usrp_rate))
        self.mmse_resampler_xx_0_0 = filter.mmse_resampler_ff(0, (audio_rate/usrp_rate))
        self.mmse_resampler_xx_0 = filter.mmse_resampler_cc(0, (744187.5/tx_rate))
        self.low_pass_filter_0 = filter.interp_fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                audio_rate,
                5000,
                1000,
                window.WIN_HAMMING,
                6.76))
        self.gr_unpack_k_bits_bb_0 = blocks.unpack_k_bits_bb(2)
        self.gr_sub_xx_0 = blocks.sub_ff(1)
        self.gr_sig_source_x_0_1 = analog.sig_source_f(usrp_rate, analog.GR_COS_WAVE, 19e3, pilot_gain, 0, 0)
        self.gr_sig_source_x_0_0 = analog.sig_source_f(380e3, analog.GR_SIN_WAVE, 57e3, rds_gain, 0, 0)
        self.gr_multiply_xx_1 = blocks.multiply_vff(1)
        self.gr_multiply_xx_0 = blocks.multiply_vff(1)
        self.gr_multiply_xx_0.set_max_output_buffer(4096)
        self.gr_map_bb_1 = digital.map_bb([1,2])
        self.gr_map_bb_1.set_max_output_buffer(4096)
        self.gr_frequency_modulator_fc_0 = analog.frequency_modulator_fc((2*math.pi*fm_max_dev/usrp_rate))
        self.gr_diff_encoder_bb_0 = digital.diff_encoder_bb(2, digital.DIFF_DIFFERENTIAL)
        self.gr_diff_encoder_bb_0.set_max_output_buffer(4096)
        self.gr_add_xx_1 = blocks.add_vff(1)
        self.gr_add_xx_0 = blocks.add_vff(1)
        self.fft_vxx_0 = fft.fft_vcc(2048, False, window.rectangular(2048), True, 1)
        self.fft_filter_xxx_6 = filter.fft_filter_fff(1, rds_taps, 1)
        self.fft_filter_xxx_6.declare_sample_delay(0)
        self.fft_filter_xxx_6.set_max_output_buffer((len(rds_taps)*4))
        self.fft_filter_xxx_5 = filter.fft_filter_ccc(1, lpf_taps, threads)
        self.fft_filter_xxx_5.declare_sample_delay(0)
        self.fft_filter_xxx_4 = filter.fft_filter_fff(1, bb_clip_taps, threads)
        self.fft_filter_xxx_4.declare_sample_delay(0)
        self.fft_filter_xxx_3_0 = filter.fft_filter_fff(1, emphasis_clip_taps, threads)
        self.fft_filter_xxx_3_0.declare_sample_delay(0)
        self.fft_filter_xxx_3 = filter.fft_filter_fff(1, emphasis_clip_taps, threads)
        self.fft_filter_xxx_3.declare_sample_delay(0)
        self.fft_filter_xxx_2 = filter.fft_filter_fff(1, pilot_taps, threads)
        self.fft_filter_xxx_2.declare_sample_delay(0)
        self.fft_filter_xxx_1 = filter.fft_filter_fff(1, bpf_taps_sca, 1)
        self.fft_filter_xxx_1.declare_sample_delay(0)
        self.fft_filter_xxx_0_1 = filter.fft_filter_fff(1, a_lpf_taps_sca, threads)
        self.fft_filter_xxx_0_1.declare_sample_delay(0)
        self.fft_filter_xxx_0_0 = filter.fft_filter_fff(1, a_lpf_taps, threads)
        self.fft_filter_xxx_0_0.declare_sample_delay(0)
        self.fft_filter_xxx_0 = filter.fft_filter_fff(1, a_lpf_taps, threads)
        self.fft_filter_xxx_0.declare_sample_delay(0)
        self.digital_chunks_to_symbols_xx_0 = digital.chunks_to_symbols_bf([-1, 1], 1)
        self.digital_chunks_to_symbols_xx_0.set_max_output_buffer(4096)
        self._clip_level_range = Range(0, 1, 0.001, 0.5, 200)
        self._clip_level_win = RangeWidget(self._clip_level_range, self.set_clip_level, "AF Clip Level", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._clip_level_win)
        self.blocks_wavfile_source_0_1_0_0_3 = blocks.wavfile_source('flag8_1.wav', True)
        self.blocks_wavfile_source_0_1_0_0_2 = blocks.wavfile_source('flag8_4.wav', True)
        self.blocks_wavfile_source_0_1_0_0_1 = blocks.wavfile_source('flag8_2.wav', True)
        self.blocks_wavfile_source_0_1_0_0_0 = blocks.wavfile_source('flag6.wav', True)
        self.blocks_wavfile_source_0_1_0_0 = blocks.wavfile_source('flag2.wav', True)
        self.blocks_wavfile_source_0_1_0 = blocks.wavfile_source('flag8_3.wav', True)
        self.blocks_wavfile_source_0_1 = blocks.wavfile_source('flag9.wav', True)
        self.blocks_vector_to_streams_0_1_0_0 = blocks.vector_to_streams(gr.sizeof_float*1, 2)
        self.blocks_vector_to_streams_0_0 = blocks.vector_to_streams(gr.sizeof_float*1, 2)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, 2048)
        self.blocks_vector_source_x_0 = blocks.vector_source_c([math.sin(math.pi / 2 * i / 112) for i in range(112)] + [1] * (2048-112) + [math.cos(math.pi / 2 * i / 112) for i in range(112)], True, 1, [])
        self.blocks_throttle2_0_0 = blocks.throttle( gr.sizeof_float*2, audio_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * audio_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_float*2, audio_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * audio_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_stream_to_vector_0_0_0 = blocks.stream_to_vector(gr.sizeof_float*1, int(decim))
        self.blocks_stream_to_vector_0_0 = blocks.stream_to_vector(gr.sizeof_float*1, int(decim))
        self.blocks_repeat_0 = blocks.repeat(gr.sizeof_gr_complex*2048, 2)
        self.blocks_nlog10_ff_0_1 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_nlog10_ff_0_0 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_nlog10_ff_0 = blocks.nlog10_ff(10, 1, 0)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_xx_7 = blocks.multiply_const_ff(2, 1)
        self.blocks_multiply_const_xx_6 = blocks.multiply_const_ff(0.5, 1)
        self.blocks_multiply_const_xx_5 = blocks.multiply_const_cc(10**(BB_gain/10), 1)
        self.blocks_multiply_const_xx_4_0 = blocks.multiply_const_ff(diff_gain, 1)
        self.blocks_multiply_const_xx_4 = blocks.multiply_const_ff(sum_gain, 1)
        self.blocks_multiply_const_xx_3 = blocks.multiply_const_ff(0.5, 1)
        self.blocks_multiply_const_xx_2 = blocks.multiply_const_ff(1/decim, 1)
        self.blocks_multiply_const_xx_1 = blocks.multiply_const_cc(ana_gain, 1)
        self.blocks_multiply_const_xx_0_0_0 = blocks.multiply_const_ff(1, 1)
        self.blocks_multiply_const_xx_0_0 = blocks.multiply_const_ff(audio_gain, 1)
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_ff(audio_gain, 1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(nrsc_gain)
        self.blocks_max_xx_0_0_0 = blocks.max_ff(int(decim), 1)
        self.blocks_max_xx_0_0 = blocks.max_ff(int(decim), 1)
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_float*1, 1)
        self.blocks_keep_m_in_n_0 = blocks.keep_m_in_n(gr.sizeof_gr_complex, 2160, 4096, 0)
        self.blocks_integrate_xx_0 = blocks.integrate_ff(int(decim), 1)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_delay_2_0 = blocks.delay(gr.sizeof_float*2, (int(44100*ana_delay)))
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, ((len(pilot_taps) - 1) // 2))
        self.blocks_conjugate_cc_0 = blocks.conjugate_cc()
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.blocks_add_xx_1_0_1 = blocks.add_vff(1)
        self.blocks_add_xx_1_0_0 = blocks.add_vff(1)
        self.blocks_add_xx_0_0 = blocks.add_vcc(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.blocks_add_const_vxx_0 = blocks.add_const_cc(dc_corr)
        self.blocks_add_const_vxx_0.set_min_output_buffer((tx_rate*1))
        self.blocks_abs_xx_1 = blocks.abs_ff(1)
        self.blocks_abs_xx_0 = blocks.abs_ff(1)
        self.analog_sig_source_x_1 = analog.sig_source_f(usrp_rate, analog.GR_COS_WAVE, 67e3, 1, 0, 0)
        self.analog_sig_source_x_0_6 = analog.sig_source_c(audio_rate, analog.GR_COS_WAVE, (audio_rate/(4*8)), 1, 0, 0)
        self.analog_rail_ff_1_0 = analog.rail_ff((-bbrail), bbrail)
        self.analog_rail_ff_1 = analog.rail_ff((-bbrail), bbrail)
        self.analog_rail_ff_0_0 = analog.rail_ff((-afrail), afrail)
        self.analog_rail_ff_0 = analog.rail_ff((-afrail), afrail)
        self.analog_fm_preemph_0_1 = analog.fm_preemph(fs=usrp_rate, tau=(75e-6), fh=5e3)
        self.analog_fm_preemph_0_0 = analog.fm_preemph(fs=usrp_rate, tau=(75e-6), fh=15e3)
        self.analog_fm_preemph_0 = analog.fm_preemph(fs=usrp_rate, tau=(75e-6), fh=15e3)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.network_socket_pdu_0, 'pdus'), (self.rds_encoder_0, 'rds in'))
        self.msg_connect((self.network_socket_pdu_0_1, 'pdus'), (self.nrsc5_psd_encoder_0, 'set_meta'))
        self.msg_connect((self.network_socket_pdu_0_1_0_0_0, 'pdus'), (self.nrsc5_lot_encoder_0_0_0_0, 'file'))
        self.msg_connect((self.network_socket_pdu_0_1_1, 'pdus'), (self.nrsc5_psd_encoder_0_0_0_0, 'set_meta'))
        self.msg_connect((self.nrsc5_l1_fm_encoder_mp3_0, 'clock'), (self.nrsc5_psd_encoder_0, 'clock'))
        self.msg_connect((self.nrsc5_l1_fm_encoder_mp3_0, 'clock'), (self.nrsc5_psd_encoder_0_0, 'clock'))
        self.msg_connect((self.nrsc5_l1_fm_encoder_mp3_0, 'clock'), (self.nrsc5_psd_encoder_0_0_0, 'clock'))
        self.msg_connect((self.nrsc5_l1_fm_encoder_mp3_0, 'clock'), (self.nrsc5_psd_encoder_0_0_0_0, 'clock'))
        self.msg_connect((self.nrsc5_l1_fm_encoder_mp3_0, 'clock'), (self.nrsc5_psd_encoder_0_1, 'clock'))
        self.msg_connect((self.nrsc5_l1_fm_encoder_mp3_0, 'clock'), (self.nrsc5_psd_encoder_0_1_0, 'clock'))
        self.msg_connect((self.nrsc5_l1_fm_encoder_mp3_0, 'clock'), (self.nrsc5_psd_encoder_0_1_1, 'clock'))
        self.msg_connect((self.nrsc5_l1_fm_encoder_mp3_0, 'clock'), (self.nrsc5_psd_encoder_0_1_1_0, 'clock'))
        self.msg_connect((self.nrsc5_l2_encoder_0, 'ready'), (self.nrsc5_lot_encoder_0, 'ready'))
        self.msg_connect((self.nrsc5_l2_encoder_0, 'ready'), (self.nrsc5_lot_encoder_0_0, 'ready'))
        self.msg_connect((self.nrsc5_l2_encoder_0, 'ready'), (self.nrsc5_lot_encoder_0_0_0_0, 'ready'))
        self.msg_connect((self.nrsc5_l2_encoder_0, 'ready'), (self.nrsc5_lot_encoder_0_3, 'ready'))
        self.msg_connect((self.nrsc5_l2_encoder_0, 'ready'), (self.nrsc5_sis_encoder_0, 'ready'))
        self.msg_connect((self.nrsc5_l2_encoder_0_0, 'ready'), (self.nrsc5_lot_encoder_0_2, 'ready'))
        self.msg_connect((self.nrsc5_l2_encoder_0_0, 'ready'), (self.nrsc5_lot_encoder_0_2_0, 'ready'))
        self.msg_connect((self.nrsc5_l2_encoder_0_0, 'ready'), (self.nrsc5_lot_encoder_0_2_0_0, 'ready'))
        self.msg_connect((self.nrsc5_l2_encoder_0_0, 'ready'), (self.nrsc5_lot_encoder_0_2_0_0_0, 'ready'))
        self.msg_connect((self.nrsc5_lot_encoder_0, 'aas'), (self.nrsc5_l2_encoder_0, 'aas'))
        self.msg_connect((self.nrsc5_lot_encoder_0_0, 'aas'), (self.nrsc5_l2_encoder_0, 'aas'))
        self.msg_connect((self.nrsc5_lot_encoder_0_0_0_0, 'aas'), (self.nrsc5_l2_encoder_0, 'aas'))
        self.msg_connect((self.nrsc5_lot_encoder_0_2, 'aas'), (self.nrsc5_l2_encoder_0_0, 'aas'))
        self.msg_connect((self.nrsc5_lot_encoder_0_2_0, 'aas'), (self.nrsc5_l2_encoder_0_0, 'aas'))
        self.msg_connect((self.nrsc5_lot_encoder_0_2_0_0, 'aas'), (self.nrsc5_l2_encoder_0_0, 'aas'))
        self.msg_connect((self.nrsc5_lot_encoder_0_2_0_0_0, 'aas'), (self.nrsc5_l2_encoder_0_0, 'aas'))
        self.msg_connect((self.nrsc5_lot_encoder_0_3, 'aas'), (self.nrsc5_l2_encoder_0, 'aas'))
        self.msg_connect((self.nrsc5_sis_encoder_0, 'aas'), (self.nrsc5_l2_encoder_0, 'aas'))
        self.connect((self.analog_fm_preemph_0, 0), (self.gr_add_xx_0, 1))
        self.connect((self.analog_fm_preemph_0, 0), (self.gr_sub_xx_0, 1))
        self.connect((self.analog_fm_preemph_0_0, 0), (self.gr_add_xx_0, 0))
        self.connect((self.analog_fm_preemph_0_0, 0), (self.gr_sub_xx_0, 0))
        self.connect((self.analog_fm_preemph_0_1, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.analog_rail_ff_0, 0), (self.fft_filter_xxx_3_0, 0))
        self.connect((self.analog_rail_ff_0_0, 0), (self.fft_filter_xxx_3, 0))
        self.connect((self.analog_rail_ff_1, 0), (self.fft_filter_xxx_4, 0))
        self.connect((self.analog_rail_ff_1_0, 0), (self.gr_add_xx_1, 2))
        self.connect((self.analog_sig_source_x_0_6, 0), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.analog_sig_source_x_1, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_abs_xx_0, 0), (self.blocks_stream_to_vector_0_0, 0))
        self.connect((self.blocks_abs_xx_1, 0), (self.fft_filter_xxx_2, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.osmosdr_sink_0, 0))
        self.connect((self.blocks_add_const_vxx_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_rail_ff_1, 0))
        self.connect((self.blocks_add_xx_0_0, 0), (self.blocks_multiply_const_xx_5, 0))
        self.connect((self.blocks_add_xx_1_0_0, 0), (self.blocks_multiply_const_xx_6, 0))
        self.connect((self.blocks_add_xx_1_0_1, 0), (self.blocks_multiply_const_xx_3, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_integrate_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_stream_to_vector_0_0_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.mmse_resampler_xx_1, 0))
        self.connect((self.blocks_conjugate_cc_0, 0), (self.mmse_resampler_xx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.gr_add_xx_1, 1))
        self.connect((self.blocks_delay_2_0, 0), (self.blocks_vector_to_streams_0_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.blocks_nlog10_ff_0, 0))
        self.connect((self.blocks_integrate_xx_0, 0), (self.blocks_multiply_const_xx_2, 0))
        self.connect((self.blocks_keep_m_in_n_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.blocks_multiply_const_xx_7, 0))
        self.connect((self.blocks_max_xx_0_0, 0), (self.qtgui_number_sink_0, 0))
        self.connect((self.blocks_max_xx_0_0_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_max_xx_0_0_0, 0), (self.blocks_nlog10_ff_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.analog_fm_preemph_0, 0))
        self.connect((self.blocks_multiply_const_xx_0_0, 0), (self.analog_fm_preemph_0_0, 0))
        self.connect((self.blocks_multiply_const_xx_0_0_0, 0), (self.analog_fm_preemph_0_1, 0))
        self.connect((self.blocks_multiply_const_xx_1, 0), (self.blocks_add_xx_0_0, 1))
        self.connect((self.blocks_multiply_const_xx_2, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.blocks_multiply_const_xx_2, 0), (self.blocks_nlog10_ff_0_1, 0))
        self.connect((self.blocks_multiply_const_xx_3, 0), (self.nrsc5_hdc_encoder_0, 0))
        self.connect((self.blocks_multiply_const_xx_4, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_xx_4, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_multiply_const_xx_4_0, 0), (self.gr_multiply_xx_1, 1))
        self.connect((self.blocks_multiply_const_xx_4_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_multiply_const_xx_5, 0), (self.blocks_add_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_xx_6, 0), (self.nrsc5_hdc_encoder_0_0_1, 0))
        self.connect((self.blocks_multiply_const_xx_7, 0), (self.nrsc5_hdc_encoder_0_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_conjugate_cc_0, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.fft_filter_xxx_1, 0))
        self.connect((self.blocks_nlog10_ff_0, 0), (self.qtgui_number_sink_0_0, 0))
        self.connect((self.blocks_nlog10_ff_0_0, 0), (self.qtgui_number_sink_0_0, 1))
        self.connect((self.blocks_nlog10_ff_0_1, 0), (self.qtgui_number_sink_0_0, 2))
        self.connect((self.blocks_repeat_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0, 0), (self.blocks_max_xx_0_0, 0))
        self.connect((self.blocks_stream_to_vector_0_0_0, 0), (self.blocks_max_xx_0_0_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_vector_to_streams_0_1_0_0, 0))
        self.connect((self.blocks_throttle2_0_0, 0), (self.blocks_delay_2_0, 0))
        self.connect((self.blocks_vector_source_x_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.blocks_keep_m_in_n_0, 0))
        self.connect((self.blocks_vector_to_streams_0_0, 0), (self.fft_filter_xxx_0, 0))
        self.connect((self.blocks_vector_to_streams_0_0, 1), (self.fft_filter_xxx_0_0, 0))
        self.connect((self.blocks_vector_to_streams_0_1_0_0, 0), (self.blocks_add_xx_1_0_1, 0))
        self.connect((self.blocks_vector_to_streams_0_1_0_0, 1), (self.blocks_add_xx_1_0_1, 1))
        self.connect((self.blocks_wavfile_source_0_1, 0), (self.fft_filter_xxx_0_1, 0))
        self.connect((self.blocks_wavfile_source_0_1_0, 0), (self.nrsc5_hdc_encoder_0_1, 0))
        self.connect((self.blocks_wavfile_source_0_1_0_0, 1), (self.blocks_add_xx_1_0_0, 1))
        self.connect((self.blocks_wavfile_source_0_1_0_0, 0), (self.blocks_add_xx_1_0_0, 0))
        self.connect((self.blocks_wavfile_source_0_1_0_0_0, 0), (self.nrsc5_hdc_encoder_0_0_0, 0))
        self.connect((self.blocks_wavfile_source_0_1_0_0_1, 0), (self.nrsc5_hdc_encoder_0_1_0, 0))
        self.connect((self.blocks_wavfile_source_0_1_0_0_2, 0), (self.nrsc5_hdc_encoder_0_1_0_0, 0))
        self.connect((self.blocks_wavfile_source_0_1_0_0_3, 0), (self.nrsc5_hdc_encoder_0_1_0_0_0, 0))
        self.connect((self.digital_chunks_to_symbols_xx_0, 0), (self.root_raised_cosine_filter_0, 0))
        self.connect((self.fft_filter_xxx_0, 0), (self.mmse_resampler_xx_0_0, 0))
        self.connect((self.fft_filter_xxx_0_0, 0), (self.mmse_resampler_xx_0_0_0, 0))
        self.connect((self.fft_filter_xxx_0_1, 0), (self.mmse_resampler_xx_0_0_3, 0))
        self.connect((self.fft_filter_xxx_1, 0), (self.gr_add_xx_1, 3))
        self.connect((self.fft_filter_xxx_2, 0), (self.gr_multiply_xx_1, 0))
        self.connect((self.fft_filter_xxx_3, 0), (self.blocks_multiply_const_xx_4, 0))
        self.connect((self.fft_filter_xxx_3_0, 0), (self.blocks_multiply_const_xx_4_0, 0))
        self.connect((self.fft_filter_xxx_4, 0), (self.analog_rail_ff_1_0, 0))
        self.connect((self.fft_filter_xxx_5, 0), (self.blocks_multiply_const_xx_1, 0))
        self.connect((self.fft_filter_xxx_6, 0), (self.gr_add_xx_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_repeat_0, 0))
        self.connect((self.gr_add_xx_0, 0), (self.analog_rail_ff_0_0, 0))
        self.connect((self.gr_add_xx_1, 0), (self.blocks_abs_xx_0, 0))
        self.connect((self.gr_add_xx_1, 0), (self.gr_frequency_modulator_fc_0, 0))
        self.connect((self.gr_add_xx_1, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.gr_add_xx_1, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.gr_add_xx_1, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.gr_diff_encoder_bb_0, 0), (self.gr_map_bb_1, 0))
        self.connect((self.gr_frequency_modulator_fc_0, 0), (self.mmse_resampler_xx_0_0_1, 0))
        self.connect((self.gr_map_bb_1, 0), (self.gr_unpack_k_bits_bb_0, 0))
        self.connect((self.gr_multiply_xx_0, 0), (self.mmse_resampler_xx_0_0_2, 0))
        self.connect((self.gr_multiply_xx_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.gr_sig_source_x_0_0, 0), (self.gr_multiply_xx_0, 0))
        self.connect((self.gr_sig_source_x_0_1, 0), (self.blocks_abs_xx_1, 0))
        self.connect((self.gr_sig_source_x_0_1, 0), (self.blocks_delay_0, 0))
        self.connect((self.gr_sub_xx_0, 0), (self.analog_rail_ff_0, 0))
        self.connect((self.gr_unpack_k_bits_bb_0, 0), (self.digital_chunks_to_symbols_xx_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.mmse_resampler_xx_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.mmse_resampler_xx_0_0, 0), (self.blocks_multiply_const_xx_0_0, 0))
        self.connect((self.mmse_resampler_xx_0_0_0, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.mmse_resampler_xx_0_0_1, 0), (self.fft_filter_xxx_5, 0))
        self.connect((self.mmse_resampler_xx_0_0_2, 0), (self.fft_filter_xxx_6, 0))
        self.connect((self.mmse_resampler_xx_0_0_3, 0), (self.blocks_multiply_const_xx_0_0_0, 0))
        self.connect((self.mmse_resampler_xx_1, 0), (self.low_pass_filter_0, 0))
        self.connect((self.nrsc5_hdc_encoder_0, 0), (self.nrsc5_l2_encoder_0, 0))
        self.connect((self.nrsc5_hdc_encoder_0_0, 0), (self.nrsc5_l2_encoder_0, 5))
        self.connect((self.nrsc5_hdc_encoder_0_0_0, 0), (self.nrsc5_l2_encoder_0_0, 0))
        self.connect((self.nrsc5_hdc_encoder_0_0_1, 0), (self.nrsc5_l2_encoder_0_0, 1))
        self.connect((self.nrsc5_hdc_encoder_0_1, 0), (self.nrsc5_l2_encoder_0, 1))
        self.connect((self.nrsc5_hdc_encoder_0_1_0, 0), (self.nrsc5_l2_encoder_0, 2))
        self.connect((self.nrsc5_hdc_encoder_0_1_0_0, 0), (self.nrsc5_l2_encoder_0, 3))
        self.connect((self.nrsc5_hdc_encoder_0_1_0_0_0, 0), (self.nrsc5_l2_encoder_0, 4))
        self.connect((self.nrsc5_l1_fm_encoder_mp3_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.nrsc5_l2_encoder_0, 0), (self.nrsc5_l1_fm_encoder_mp3_0, 0))
        self.connect((self.nrsc5_l2_encoder_0_0, 0), (self.nrsc5_l1_fm_encoder_mp3_0, 1))
        self.connect((self.nrsc5_psd_encoder_0, 0), (self.nrsc5_l2_encoder_0, 6))
        self.connect((self.nrsc5_psd_encoder_0_0, 0), (self.nrsc5_l2_encoder_0, 11))
        self.connect((self.nrsc5_psd_encoder_0_0_0, 0), (self.nrsc5_l2_encoder_0_0, 2))
        self.connect((self.nrsc5_psd_encoder_0_0_0_0, 0), (self.nrsc5_l2_encoder_0_0, 3))
        self.connect((self.nrsc5_psd_encoder_0_1, 0), (self.nrsc5_l2_encoder_0, 7))
        self.connect((self.nrsc5_psd_encoder_0_1_0, 0), (self.nrsc5_l2_encoder_0, 8))
        self.connect((self.nrsc5_psd_encoder_0_1_1, 0), (self.nrsc5_l2_encoder_0, 9))
        self.connect((self.nrsc5_psd_encoder_0_1_1_0, 0), (self.nrsc5_l2_encoder_0, 10))
        self.connect((self.nrsc5_sis_encoder_0, 0), (self.nrsc5_l1_fm_encoder_mp3_0, 2))
        self.connect((self.paint_image_source_0, 0), (self.paint_paint_bc_0, 0))
        self.connect((self.paint_paint_bc_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.rds_encoder_0, 0), (self.gr_diff_encoder_bb_0, 0))
        self.connect((self.root_raised_cosine_filter_0, 0), (self.gr_multiply_xx_0, 1))
        self.connect((self.zeromq_sub_source_0_0, 0), (self.blocks_throttle2_0_0, 0))
        self.connect((self.zeromq_sub_source_0_0_0, 0), (self.blocks_throttle2_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "rds_tx_nrsc5")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_ana_delay(self):
        return self.ana_delay

    def set_ana_delay(self, ana_delay):
        self.ana_delay = ana_delay
        self.blocks_delay_2_0.set_dly(int((int(44100*self.ana_delay))))

    def get_bb_gain(self):
        return self.bb_gain

    def set_bb_gain(self, bb_gain):
        self.bb_gain = bb_gain
        self.set_BB_gain(self.bb_gain)

    def get_dc_offset(self):
        return self.dc_offset

    def set_dc_offset(self, dc_offset):
        self.dc_offset = dc_offset
        self.set_dc_corr(self.dc_offset)

    def get_digi_delay(self):
        return self.digi_delay

    def set_digi_delay(self, digi_delay):
        self.digi_delay = digi_delay

    def get_tx_rate(self):
        return self.tx_rate

    def set_tx_rate(self, tx_rate):
        self.tx_rate = tx_rate
        self.set_lpf_taps(firdes.low_pass(1.0, self.tx_rate, 105e3, 10e3, window.WIN_HAMMING, 6.76))
        self.mmse_resampler_xx_0.set_resamp_ratio((744187.5/self.tx_rate))
        self.mmse_resampler_xx_0_0_1.set_resamp_ratio((self.usrp_rate/self.tx_rate))
        self.osmosdr_sink_0.set_sample_rate(self.tx_rate)
        self.qtgui_sink_x_0.set_frequency_range(self.freq, self.tx_rate)

    def get_rds_gain(self):
        return self.rds_gain

    def set_rds_gain(self, rds_gain):
        self.rds_gain = rds_gain
        self.set_bbrail((1-self.pilot_gain-self.rds_gain))
        self.set_input_gain((0.5-self.rds_gain/2-self.pilot_gain/2)*1.95)
        self.gr_sig_source_x_0_0.set_amplitude(self.rds_gain)

    def get_pilot_gain(self):
        return self.pilot_gain

    def set_pilot_gain(self, pilot_gain):
        self.pilot_gain = pilot_gain
        self.set_bbrail((1-self.pilot_gain-self.rds_gain))
        self.set_input_gain((0.5-self.rds_gain/2-self.pilot_gain/2)*1.95)
        self.set_pilot_taps(firdes.band_pass(1/self.pilot_gain*2, self.usrp_rate, 37980, 38020, 1000, window.WIN_HAMMING, 6.76))
        self.gr_sig_source_x_0_1.set_amplitude(self.pilot_gain)

    def get_usrp_rate(self):
        return self.usrp_rate

    def set_usrp_rate(self, usrp_rate):
        self.usrp_rate = usrp_rate
        self.set_bb_clip_taps(firdes.low_pass(1, self.usrp_rate, 53e3, 2e3, window.WIN_HAMMING, 6.76))
        self.set_bpf_taps_sca(firdes.band_pass(1.0, self.usrp_rate, 67e3, 67e3+5e3, 1000, window.WIN_HAMMING, 6.76))
        self.set_emphasis_clip_taps(firdes.low_pass(self.input_gain, self.usrp_rate, 15e3, 1e3, window.WIN_HAMMING, 6.76))
        self.set_pilot_taps(firdes.band_pass(1/self.pilot_gain*2, self.usrp_rate, 37980, 38020, 1000, window.WIN_HAMMING, 6.76))
        self.set_rds_taps(firdes.band_pass(1.0, self.usrp_rate, 55e3, 59e3, 300, window.WIN_BLACKMAN, 6.76))
        self.analog_sig_source_x_1.set_sampling_freq(self.usrp_rate)
        self.gr_frequency_modulator_fc_0.set_sensitivity((2*math.pi*self.fm_max_dev/self.usrp_rate))
        self.gr_sig_source_x_0_1.set_sampling_freq(self.usrp_rate)
        self.mmse_resampler_xx_0_0.set_resamp_ratio((self.audio_rate/self.usrp_rate))
        self.mmse_resampler_xx_0_0_0.set_resamp_ratio((self.audio_rate/self.usrp_rate))
        self.mmse_resampler_xx_0_0_1.set_resamp_ratio((self.usrp_rate/self.tx_rate))
        self.mmse_resampler_xx_0_0_2.set_resamp_ratio((380e3/self.usrp_rate))
        self.mmse_resampler_xx_0_0_3.set_resamp_ratio((self.audio_rate/self.usrp_rate))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.usrp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.usrp_rate)
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.usrp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.usrp_rate)

    def get_input_gain(self):
        return self.input_gain

    def set_input_gain(self, input_gain):
        self.input_gain = input_gain
        self.set_emphasis_clip_taps(firdes.low_pass(self.input_gain, self.usrp_rate, 15e3, 1e3, window.WIN_HAMMING, 6.76))

    def get_audio_rate(self):
        return self.audio_rate

    def set_audio_rate(self, audio_rate):
        self.audio_rate = audio_rate
        self.set_a_lpf_taps(firdes.low_pass(0.5, self.audio_rate, 16e3, 1e3, window.WIN_HAMMING, 6.76))
        self.set_a_lpf_taps_sca(firdes.low_pass(0.5, self.audio_rate, 5e3, 1e3, window.WIN_HAMMING, 6.76))
        self.analog_sig_source_x_0_6.set_sampling_freq(self.audio_rate)
        self.analog_sig_source_x_0_6.set_frequency((self.audio_rate/(4*8)))
        self.blocks_throttle2_0.set_sample_rate(self.audio_rate)
        self.blocks_throttle2_0_0.set_sample_rate(self.audio_rate)
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.audio_rate, 5000, 1000, window.WIN_HAMMING, 6.76))
        self.mmse_resampler_xx_0_0.set_resamp_ratio((self.audio_rate/self.usrp_rate))
        self.mmse_resampler_xx_0_0_0.set_resamp_ratio((self.audio_rate/self.usrp_rate))
        self.mmse_resampler_xx_0_0_3.set_resamp_ratio((self.audio_rate/self.usrp_rate))

    def get_threads(self):
        return self.threads

    def set_threads(self, threads):
        self.threads = threads
        self.fft_filter_xxx_0.set_nthreads(self.threads)
        self.fft_filter_xxx_0_0.set_nthreads(self.threads)
        self.fft_filter_xxx_0_1.set_nthreads(self.threads)
        self.fft_filter_xxx_2.set_nthreads(self.threads)
        self.fft_filter_xxx_3.set_nthreads(self.threads)
        self.fft_filter_xxx_3_0.set_nthreads(self.threads)
        self.fft_filter_xxx_4.set_nthreads(self.threads)
        self.fft_filter_xxx_5.set_nthreads(self.threads)

    def get_sum_gain(self):
        return self.sum_gain

    def set_sum_gain(self, sum_gain):
        self.sum_gain = sum_gain
        self.blocks_multiply_const_xx_4.set_k(self.sum_gain)

    def get_rds_taps(self):
        return self.rds_taps

    def set_rds_taps(self, rds_taps):
        self.rds_taps = rds_taps
        self.fft_filter_xxx_6.set_taps(self.rds_taps)

    def get_pilot_taps(self):
        return self.pilot_taps

    def set_pilot_taps(self, pilot_taps):
        self.pilot_taps = pilot_taps
        self.blocks_delay_0.set_dly(int(((len(self.pilot_taps) - 1) // 2)))
        self.fft_filter_xxx_2.set_taps(self.pilot_taps)

    def get_p2rate(self):
        return self.p2rate

    def set_p2rate(self, p2rate):
        self.p2rate = p2rate

    def get_p1rate(self):
        return self.p1rate

    def set_p1rate(self, p1rate):
        self.p1rate = p1rate

    def get_nrsc_gain(self):
        return self.nrsc_gain

    def set_nrsc_gain(self, nrsc_gain):
        self.nrsc_gain = nrsc_gain
        self.blocks_multiply_const_vxx_0.set_k(self.nrsc_gain)

    def get_maxpsdbuf(self):
        return self.maxpsdbuf

    def set_maxpsdbuf(self, maxpsdbuf):
        self.maxpsdbuf = maxpsdbuf

    def get_lpf_taps(self):
        return self.lpf_taps

    def set_lpf_taps(self, lpf_taps):
        self.lpf_taps = lpf_taps
        self.fft_filter_xxx_5.set_taps(self.lpf_taps)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.osmosdr_sink_0.set_center_freq(self.freq, 0)
        self.qtgui_sink_x_0.set_frequency_range(self.freq, self.tx_rate)

    def get_fm_max_dev(self):
        return self.fm_max_dev

    def set_fm_max_dev(self, fm_max_dev):
        self.fm_max_dev = fm_max_dev
        self.gr_frequency_modulator_fc_0.set_sensitivity((2*math.pi*self.fm_max_dev/self.usrp_rate))

    def get_emphasis_clip_taps(self):
        return self.emphasis_clip_taps

    def set_emphasis_clip_taps(self, emphasis_clip_taps):
        self.emphasis_clip_taps = emphasis_clip_taps
        self.fft_filter_xxx_3.set_taps(self.emphasis_clip_taps)
        self.fft_filter_xxx_3_0.set_taps(self.emphasis_clip_taps)

    def get_diff_gain(self):
        return self.diff_gain

    def set_diff_gain(self, diff_gain):
        self.diff_gain = diff_gain
        self.blocks_multiply_const_xx_4_0.set_k(self.diff_gain)

    def get_decim(self):
        return self.decim

    def set_decim(self, decim):
        self.decim = decim
        self.blocks_multiply_const_xx_2.set_k(1/self.decim)

    def get_dc_corr(self):
        return self.dc_corr

    def set_dc_corr(self, dc_corr):
        self.dc_corr = dc_corr
        self.blocks_add_const_vxx_0.set_k(self.dc_corr)

    def get_clip_level(self):
        return self.clip_level

    def set_clip_level(self, clip_level):
        self.clip_level = clip_level

    def get_bpf_taps_sca(self):
        return self.bpf_taps_sca

    def set_bpf_taps_sca(self, bpf_taps_sca):
        self.bpf_taps_sca = bpf_taps_sca
        self.fft_filter_xxx_1.set_taps(self.bpf_taps_sca)

    def get_bbrail(self):
        return self.bbrail

    def set_bbrail(self, bbrail):
        self.bbrail = bbrail
        self.analog_rail_ff_1.set_lo((-self.bbrail))
        self.analog_rail_ff_1.set_hi(self.bbrail)
        self.analog_rail_ff_1_0.set_lo((-self.bbrail))
        self.analog_rail_ff_1_0.set_hi(self.bbrail)

    def get_bb_clip_taps(self):
        return self.bb_clip_taps

    def set_bb_clip_taps(self, bb_clip_taps):
        self.bb_clip_taps = bb_clip_taps
        self.fft_filter_xxx_4.set_taps(self.bb_clip_taps)

    def get_audio_gain(self):
        return self.audio_gain

    def set_audio_gain(self, audio_gain):
        self.audio_gain = audio_gain
        self.blocks_multiply_const_xx_0.set_k(self.audio_gain)
        self.blocks_multiply_const_xx_0_0.set_k(self.audio_gain)

    def get_ana_gain(self):
        return self.ana_gain

    def set_ana_gain(self, ana_gain):
        self.ana_gain = ana_gain
        self.blocks_multiply_const_xx_1.set_k(self.ana_gain)

    def get_afrail(self):
        return self.afrail

    def set_afrail(self, afrail):
        self.afrail = afrail
        self.analog_rail_ff_0.set_lo((-self.afrail))
        self.analog_rail_ff_0.set_hi(self.afrail)
        self.analog_rail_ff_0_0.set_lo((-self.afrail))
        self.analog_rail_ff_0_0.set_hi(self.afrail)

    def get_a_lpf_taps_sca(self):
        return self.a_lpf_taps_sca

    def set_a_lpf_taps_sca(self, a_lpf_taps_sca):
        self.a_lpf_taps_sca = a_lpf_taps_sca
        self.fft_filter_xxx_0_1.set_taps(self.a_lpf_taps_sca)

    def get_a_lpf_taps(self):
        return self.a_lpf_taps

    def set_a_lpf_taps(self, a_lpf_taps):
        self.a_lpf_taps = a_lpf_taps
        self.fft_filter_xxx_0.set_taps(self.a_lpf_taps)
        self.fft_filter_xxx_0_0.set_taps(self.a_lpf_taps)

    def get_BB_gain(self):
        return self.BB_gain

    def set_BB_gain(self, BB_gain):
        self.BB_gain = BB_gain
        self.blocks_multiply_const_xx_5.set_k(10**(self.BB_gain/10))



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--ana-delay", dest="ana_delay", type=eng_float, default=eng_notation.num_to_str(float(4.5)),
        help="Set Analog Delay (sec) [default=%(default)r]")
    parser.add_argument(
        "--bb-gain", dest="bb_gain", type=eng_float, default=eng_notation.num_to_str(float((-4))),
        help="Set Baseband Gain (dB) [default=%(default)r]")
    parser.add_argument(
        "--dc-offset", dest="dc_offset", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set BB DC offset [default=%(default)r]")
    parser.add_argument(
        "--digi-delay", dest="digi_delay", type=eng_float, default=eng_notation.num_to_str(float(0)),
        help="Set Digital Delay (sec) [default=%(default)r]")
    parser.add_argument(
        "--tx-rate", dest="tx_rate", type=intx, default=2000000,
        help="Set TX Rate (Hz) [default=%(default)r]")
    return parser


def main(top_block_cls=rds_tx_nrsc5, options=None):
    if options is None:
        options = argument_parser().parse_args()
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        gr.logger("realtime").warning("Error: failed to enable real-time scheduling.")

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(ana_delay=options.ana_delay, bb_gain=options.bb_gain, dc_offset=options.dc_offset, digi_delay=options.digi_delay, tx_rate=options.tx_rate)

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
