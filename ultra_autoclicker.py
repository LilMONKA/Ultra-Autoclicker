import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
import keyboard
import time
import threading

class ClickerThread(QThread):
    update_count = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.mouse = MouseController()
        self.is_running = False
        self.clicks_per_second = 10
        self.click_button = Button.left
        self.click_type = "single"
        self.click_position = None  # None = current position
        self.total_clicks = 0
        
    def run(self):
        self.is_running = True
        self.total_clicks = 0
        
        if self.clicks_per_second >= 1000:
            # Turbo mode - no delay
            delay = 0
        else:
            delay = 1.0 / self.clicks_per_second
            
        last_update = time.time()
        
        while self.is_running:
            if self.click_position:
                self.mouse.position = self.click_position
                
            if self.click_type == "single":
                self.mouse.click(self.click_button, 1)
                self.total_clicks += 1
            elif self.click_type == "double":
                self.mouse.click(self.click_button, 2)
                self.total_clicks += 2
            elif self.click_type == "triple":
                self.mouse.click(self.click_button, 3)
                self.total_clicks += 3
                
            # Update counter every 0.1 seconds
            if time.time() - last_update > 0.1:
                self.update_count.emit(self.total_clicks)
                last_update = time.time()
                
            if delay > 0:
                time.sleep(delay)
                
    def stop(self):
        self.is_running = False


class AutoClickerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🖱️ Ultra Auto-Clicker Pro")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0d1117;
            }
            QLabel {
                color: #c9d1d9;
                font-size: 12px;
            }
            QPushButton {
                background-color: #238636;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QPushButton:pressed {
                background-color: #1a7f37;
            }
            QPushButton#stopBtn {
                background-color: #da3633;
            }
            QPushButton#stopBtn:hover {
                background-color: #e5534b;
            }
            QPushButton#stopBtn:pressed {
                background-color: #b62324;
            }
            QPushButton:disabled {
                background-color: #21262d;
                color: #484f58;
            }
            QSpinBox, QComboBox {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                padding: 8px;
                border-radius: 6px;
                font-size: 14px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #21262d;
                border: 1px solid #30363d;
            }
            QFrame#panel {
                background-color: #161b22;
                border-radius: 6px;
                border: 1px solid #30363d;
            }
            QRadioButton {
                color: #c9d1d9;
                font-size: 13px;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox {
                color: #c9d1d9;
                font-size: 13px;
            }
        """)
        
        self.clicker_thread = ClickerThread()
        self.clicker_thread.update_count.connect(self.update_click_count)
        
        # Hotkey
        self.start_hotkey = "f6"
        self.stop_hotkey = "f7"
        self.is_clicking = False
        
        self.init_ui()
        self.setup_hotkeys()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QFrame()
        header.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #238636, stop:1 #2ea043); border-radius: 8px;")
        header_layout = QVBoxLayout(header)
        
        title = QLabel("🖱️ ULTRA AUTO-CLICKER PRO")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: white; padding: 20px;")
        title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("⚡ Maximum Speed Clicking Tool")
        subtitle.setStyleSheet("font-size: 14px; color: white; padding: 0px 20px 20px 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle)
        
        main_layout.addWidget(header)
        
        # Status Display
        status_frame = QFrame()
        status_frame.setObjectName("panel")
        status_layout = QVBoxLayout(status_frame)
        
        self.status_label = QLabel("⭕ IDLE")
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #58a6ff; padding: 15px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        self.click_counter = QLabel("Total Clicks: 0")
        self.click_counter.setStyleSheet("font-size: 18px; color: #7ee787; padding: 10px;")
        self.click_counter.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.click_counter)
        
        self.cps_display = QLabel("Current CPS: 0")
        self.cps_display.setStyleSheet("font-size: 16px; color: #79c0ff; padding: 5px;")
        self.cps_display.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.cps_display)
        
        main_layout.addWidget(status_frame)
        
        # Settings Grid
        settings_grid = QGridLayout()
        settings_grid.setSpacing(15)
        
        # Click Speed
        speed_panel = QFrame()
        speed_panel.setObjectName("panel")
        speed_layout = QVBoxLayout(speed_panel)
        
        speed_title = QLabel("⚡ CLICK SPEED")
        speed_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0883e; padding: 10px;")
        speed_layout.addWidget(speed_title)
        
        speed_info = QLabel("Clicks Per Second (CPS):")
        speed_info.setStyleSheet("padding: 5px 10px;")
        speed_layout.addWidget(speed_info)
        
        self.cps_spinbox = QSpinBox()
        self.cps_spinbox.setMinimum(1)
        self.cps_spinbox.setMaximum(999999999)
        self.cps_spinbox.setValue(100)
        self.cps_spinbox.setSuffix(" CPS")
        self.cps_spinbox.setStyleSheet("padding: 12px; font-size: 16px; font-weight: bold;")
        speed_layout.addWidget(self.cps_spinbox)
        
        # Preset buttons
        presets_layout = QHBoxLayout()
        
        preset_values = [
            ("Normal", 10),
            ("Fast", 100),
            ("Turbo", 1000),
            ("ULTRA", 10000),
            ("MAX", 999999)
        ]
        
        for name, value in preset_values:
            btn = QPushButton(name)
            btn.setStyleSheet("background-color: #1f6feb; padding: 8px 12px; font-size: 11px;")
            btn.clicked.connect(lambda checked, v=value: self.cps_spinbox.setValue(v))
            presets_layout.addWidget(btn)
            
        speed_layout.addLayout(presets_layout)
        
        settings_grid.addWidget(speed_panel, 0, 0)
        
        # Click Button
        button_panel = QFrame()
        button_panel.setObjectName("panel")
        button_layout = QVBoxLayout(button_panel)
        
        button_title = QLabel("🖱️ MOUSE BUTTON")
        button_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0883e; padding: 10px;")
        button_layout.addWidget(button_title)
        
        self.left_radio = QRadioButton("Left Click")
        self.left_radio.setChecked(True)
        self.left_radio.setStyleSheet("padding: 8px 10px;")
        button_layout.addWidget(self.left_radio)
        
        self.right_radio = QRadioButton("Right Click")
        self.right_radio.setStyleSheet("padding: 8px 10px;")
        button_layout.addWidget(self.right_radio)
        
        self.middle_radio = QRadioButton("Middle Click")
        self.middle_radio.setStyleSheet("padding: 8px 10px;")
        button_layout.addWidget(self.middle_radio)
        
        button_layout.addStretch()
        
        settings_grid.addWidget(button_panel, 0, 1)
        
        # Click Type
        type_panel = QFrame()
        type_panel.setObjectName("panel")
        type_layout = QVBoxLayout(type_panel)
        
        type_title = QLabel("🎯 CLICK TYPE")
        type_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0883e; padding: 10px;")
        type_layout.addWidget(type_title)
        
        self.single_radio = QRadioButton("Single Click")
        self.single_radio.setChecked(True)
        self.single_radio.setStyleSheet("padding: 8px 10px;")
        type_layout.addWidget(self.single_radio)
        
        self.double_radio = QRadioButton("Double Click")
        self.double_radio.setStyleSheet("padding: 8px 10px;")
        type_layout.addWidget(self.double_radio)
        
        self.triple_radio = QRadioButton("Triple Click")
        self.triple_radio.setStyleSheet("padding: 8px 10px;")
        type_layout.addWidget(self.triple_radio)
        
        type_layout.addStretch()
        
        settings_grid.addWidget(type_panel, 1, 0)
        
        # Position Settings
        position_panel = QFrame()
        position_panel.setObjectName("panel")
        position_layout = QVBoxLayout(position_panel)
        
        position_title = QLabel("📍 POSITION")
        position_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0883e; padding: 10px;")
        position_layout.addWidget(position_title)
        
        self.current_pos_radio = QRadioButton("Current Mouse Position")
        self.current_pos_radio.setChecked(True)
        self.current_pos_radio.setStyleSheet("padding: 8px 10px;")
        position_layout.addWidget(self.current_pos_radio)
        
        self.fixed_pos_radio = QRadioButton("Fixed Position")
        self.fixed_pos_radio.setStyleSheet("padding: 8px 10px;")
        position_layout.addWidget(self.fixed_pos_radio)
        
        self.set_pos_btn = QPushButton("📌 Set Current Position")
        self.set_pos_btn.setEnabled(False)
        self.set_pos_btn.clicked.connect(self.set_fixed_position)
        self.set_pos_btn.setStyleSheet("background-color: #1f6feb; padding: 8px; margin: 5px;")
        position_layout.addWidget(self.set_pos_btn)
        
        self.pos_label = QLabel("Not Set")
        self.pos_label.setStyleSheet("padding: 5px 10px; color: #8b949e; font-size: 11px;")
        self.pos_label.setAlignment(Qt.AlignCenter)
        position_layout.addWidget(self.pos_label)
        
        self.fixed_pos_radio.toggled.connect(lambda: self.set_pos_btn.setEnabled(self.fixed_pos_radio.isChecked()))
        
        position_layout.addStretch()
        
        settings_grid.addWidget(position_panel, 1, 1)
        
        main_layout.addLayout(settings_grid)
        
        # Hotkeys Info
        hotkey_frame = QFrame()
        hotkey_frame.setObjectName("panel")
        hotkey_layout = QVBoxLayout(hotkey_frame)
        
        hotkey_title = QLabel("⌨️ HOTKEYS")
        hotkey_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f0883e; padding: 10px;")
        hotkey_layout.addWidget(hotkey_title)
        
        hotkey_info = QLabel(f"🟢 Start/Pause: <b>F6</b> &nbsp;&nbsp;&nbsp; 🔴 Stop: <b>F7</b>")
        hotkey_info.setStyleSheet("padding: 10px; font-size: 14px; color: #7ee787;")
        hotkey_info.setAlignment(Qt.AlignCenter)
        hotkey_layout.addWidget(hotkey_info)
        
        main_layout.addWidget(hotkey_frame)
        
        # Control Buttons
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        self.start_btn = QPushButton("▶️ START CLICKING")
        self.start_btn.setMinimumHeight(60)
        self.start_btn.setStyleSheet("font-size: 18px; background-color: #238636;")
        self.start_btn.clicked.connect(self.start_clicking)
        controls_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹️ STOP")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setMinimumHeight(60)
        self.stop_btn.setStyleSheet("font-size: 18px;")
        self.stop_btn.clicked.connect(self.stop_clicking)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Footer
        footer = QLabel("⚠️ Use responsibly • May violate game ToS • For testing purposes")
        footer.setStyleSheet("color: #8b949e; font-size: 10px; padding: 10px;")
        footer.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer)
        
    def setup_hotkeys(self):
        keyboard.add_hotkey(self.start_hotkey, self.toggle_clicking)
        keyboard.add_hotkey(self.stop_hotkey, self.stop_clicking)
        
    def set_fixed_position(self):
        mouse = MouseController()
        pos = mouse.position
        self.clicker_thread.click_position = pos
        self.pos_label.setText(f"X: {pos[0]}, Y: {pos[1]}")
        
    def toggle_clicking(self):
        if self.is_clicking:
            self.pause_clicking()
        else:
            self.start_clicking()
            
    def start_clicking(self):
        # Update settings
        self.clicker_thread.clicks_per_second = self.cps_spinbox.value()
        
        if self.left_radio.isChecked():
            self.clicker_thread.click_button = Button.left
        elif self.right_radio.isChecked():
            self.clicker_thread.click_button = Button.right
        else:
            self.clicker_thread.click_button = Button.middle
            
        if self.single_radio.isChecked():
            self.clicker_thread.click_type = "single"
        elif self.double_radio.isChecked():
            self.clicker_thread.click_type = "double"
        else:
            self.clicker_thread.click_type = "triple"
            
        if not self.current_pos_radio.isChecked():
            if self.clicker_thread.click_position is None:
                QMessageBox.warning(self, "Warning", "Please set a fixed position first!")
                return
        else:
            self.clicker_thread.click_position = None
            
        # Start clicking
        self.is_clicking = True
        self.status_label.setText("🟢 CLICKING")
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #7ee787; padding: 15px;")
        self.cps_display.setText(f"Current CPS: {self.cps_spinbox.value()}")
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.clicker_thread.start()
        
    def pause_clicking(self):
        self.clicker_thread.stop()
        self.is_clicking = False
        self.status_label.setText("⏸️ PAUSED")
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #f0883e; padding: 15px;")
        
        self.start_btn.setEnabled(True)
        self.start_btn.setText("▶️ RESUME")
        
    def stop_clicking(self):
        self.clicker_thread.stop()
        self.is_clicking = False
        self.status_label.setText("⭕ IDLE")
        self.status_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #58a6ff; padding: 15px;")
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.start_btn.setText("▶️ START CLICKING")
        
        # Reset counter
        self.click_counter.setText("Total Clicks: 0")
        self.cps_display.setText("Current CPS: 0")
        
    def update_click_count(self, count):
        self.click_counter.setText(f"Total Clicks: {count:,}")
        
    def closeEvent(self, event):
        self.clicker_thread.stop()
        keyboard.unhook_all()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AutoClickerGUI()
    window.show()
    sys.exit(app.exec_())