import sys
import os
from pathlib import Path
import pikepdf
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QLineEdit, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QByteArray, QResource
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtGui import QFont, QIcon

class DecryptThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, filename, password):
        QThread.__init__(self)
        self.filename = filename
        self.password = password

    def run(self):
        try:
            pdf = pikepdf.open(self.filename, password=self.password)
            total_pages = len(pdf.pages)
            
            new_file = self.filename.replace('.pdf', ' [Desbloqueado].pdf')
            with pikepdf.new() as new_pdf:
                for i, page in enumerate(pdf.pages):
                    new_pdf.pages.append(page)
                    self.progress.emit(int((i + 1) / total_pages * 100))
                
                new_pdf.save(new_file)
            
            pdf.close()
            self.finished.emit(new_file)
        except Exception as e:
            self.finished.emit(str(e))

class PDFDecryptor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('GABI -> Desencriptador PDF')
        #self.setWindowIcon(QIcon(':/app_icon.png'))
        self.setGeometry(100, 100, 600, 180)

        layout = QHBoxLayout()

        # Left side
        left_layout = QVBoxLayout()
        
        self.file_button = QPushButton('Seleccionar archivo PDF')
        self.file_button.clicked.connect(self.select_file)
        left_layout.addWidget(self.file_button)

        self.file_label = QLabel('No se selecciono ningun archivo')
        left_layout.addWidget(self.file_label)

        self.decrypt_button = QPushButton('Desencriptar PDF')
        self.decrypt_button.clicked.connect(self.decrypt_pdf)
        left_layout.addWidget(self.decrypt_button)

        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)

        self.status_label = QLabel('')
        left_layout.addWidget(self.status_label)

        # Créditos
        credits_label = QLabel('Desarrollado por Gabi. Email: <a href="mailto:winnstorm@gmail.com">winnstorm@gmail.com</a>')
        credits_label.setOpenExternalLinks(True)
        font = QFont()
        font.setItalic(True)
        font.setPointSize(6)
        credits_label.setFont(font)
        credits_label.setAlignment(Qt.AlignCenter)

        # Agregar el credits_label al layout izquierdo
        left_layout.addWidget(credits_label)

        # Agregar un espaciador para empujar el credits_label hacia abajo
        left_layout.addStretch()

        layout.addLayout(left_layout)

        # Right side (SVG image)
        right_layout = QVBoxLayout()
        svg_widget = QSvgWidget()
        svg_data = QByteArray(self.get_svg_data().encode('utf-8'))
        svg_widget.load(svg_data)
        svg_widget.setFixedSize(100, 100)
        right_layout.addWidget(svg_widget)
        layout.addLayout(right_layout)

        self.setLayout(layout)

    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo PDF", "", "PDF Files (*.pdf)")
        if filename:
            self.file_label.setText(filename)

    def decrypt_pdf(self):
        filename = self.file_label.text()
        if filename == 'No se selecciono ningun archivo':
            self.status_label.setText('Seleccione un archivo PDF Primero')
            return

        password = ''
        
        self.decrypt_thread = DecryptThread(filename, password)
        self.decrypt_thread.progress.connect(self.update_progress)
        self.decrypt_thread.finished.connect(self.decryption_finished)
        self.decrypt_thread.start()

        self.decrypt_button.setEnabled(False)
        self.status_label.setText('Haciendo magia...')

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def decryption_finished(self, result):
        self.decrypt_button.setEnabled(True)
        if result.endswith('.pdf'):
            self.status_label.setText(f'Desencriptado con exito. Archivo guardado en: {result}')
            os.startfile(str(Path(result).parent))
        else:
            self.status_label.setText(f'Desencriptado fallido: {result}')

    def get_svg_data(self):
        return '''
        <svg version="1.0" xmlns="http://www.w3.org/2000/svg"
 width="512.000000pt" height="512.000000pt" viewBox="0 0 512.000000 512.000000"
 preserveAspectRatio="xMidYMid meet">

<g transform="translate(0.000000,512.000000) scale(0.100000,-0.100000)"
fill="#000000" stroke="none">
<path d="M2321 5109 c-481 -43 -982 -247 -1367 -556 -513 -414 -839 -998 -936
-1678 -20 -140 -17 -504 6 -660 39 -278 121 -541 247 -794 331 -667 931 -1152
1657 -1340 509 -132 1067 -98 1560 94 349 137 639 330 907 606 205 210 340
404 465 663 119 246 190 474 232 741 31 200 31 550 0 750 -43 273 -114 500
-237 750 -132 270 -270 461 -489 680 -224 223 -403 353 -677 489 -422 210
-890 297 -1368 255z m159 -228 l0 -78 -82 -7 c-193 -16 -386 -56 -562 -116
-50 -16 -91 -30 -94 -30 -9 0 -62 134 -55 140 12 11 214 76 308 99 113 27 262
51 380 60 55 5 101 9 103 10 1 0 2 -34 2 -78z m370 58 c52 -6 149 -22 215 -36
119 -25 352 -96 368 -112 7 -7 -31 -112 -49 -139 -1 -2 -58 15 -127 37 -151
49 -331 86 -494 102 l-123 12 0 78 0 78 58 -5 c31 -3 100 -9 152 -15z m-1292
-289 l30 -69 -93 -51 c-126 -67 -250 -152 -366 -248 l-97 -80 -53 54 c-53 53
-53 53 -33 75 34 38 197 165 290 227 82 55 270 162 285 162 3 0 20 -31 37 -70z
m2154 11 c136 -76 233 -141 356 -241 140 -112 135 -101 72 -165 l-54 -55 -36
34 c-101 95 -318 246 -442 307 -38 18 -68 39 -68 45 0 18 51 134 59 134 4 0
55 -27 113 -59z m-842 -47 c624 -94 1168 -466 1489 -1016 193 -331 297 -754
277 -1123 -19 -346 -101 -635 -259 -920 -207 -374 -517 -668 -902 -857 -622
-305 -1338 -285 -1935 53 -333 189 -612 470 -794 799 -200 361 -287 760 -257
1180 18 259 111 575 238 810 105 193 226 352 389 510 341 330 772 531 1244
579 124 13 378 5 510 -15z m-2003 -476 l52 -51 -58 -66 c-109 -124 -194 -247
-280 -403 -47 -86 -35 -82 -134 -39 l-49 21 47 88 c55 101 138 232 203 317 57
75 152 185 160 185 4 0 30 -23 59 -52z m3523 -30 c98 -114 234 -319 308 -465
34 -67 62 -126 62 -131 0 -9 -139 -68 -143 -61 -1 2 -28 57 -61 121 -71 143
-168 291 -274 419 l-80 96 51 52 c29 28 55 51 59 51 4 0 39 -37 78 -82z
m-3979 -691 l66 -29 -30 -81 c-31 -89 -87 -292 -87 -319 0 -11 12 -18 41 -23
38 -7 41 -9 36 -35 -3 -15 -9 -50 -13 -78 l-6 -51 -43 6 -43 5 -7 -86 -7 -86
-78 0 -79 0 5 58 c22 266 62 464 136 670 17 46 33 82 37 80 4 -2 36 -16 72
-31z m4437 -147 c53 -164 88 -351 100 -527 l7 -103 -76 0 -76 0 -7 88 c-10
134 -44 325 -81 452 -18 63 -32 115 -32 116 18 12 134 51 138 46 4 -4 16 -36
27 -72z m-4515 -949 c14 -136 71 -405 102 -482 4 -12 -10 -22 -62 -42 -37 -15
-70 -24 -74 -19 -4 4 -16 36 -27 72 -53 164 -88 351 -100 528 l-7 102 75 0 76
0 17 -159z m4621 102 c-19 -236 -54 -422 -115 -607 -22 -67 -43 -127 -47 -134
-6 -9 -25 -5 -79 19 l-70 31 40 114 c22 62 37 120 34 127 -3 8 -21 17 -40 21
l-34 6 18 76 c10 42 20 78 21 80 2 1 20 -1 41 -6 20 -4 39 -4 42 0 3 4 13 80
22 169 l17 161 77 0 78 0 -5 -57z m-4392 -871 c70 -143 170 -295 276 -423 l80
-97 -53 -52 c-31 -31 -58 -49 -65 -45 -26 16 -169 198 -240 306 -70 106 -200
344 -200 367 0 8 123 61 140 61 3 0 31 -53 62 -117z m4105 -8 l55 -24 -47 -88
c-67 -124 -159 -261 -252 -378 -115 -141 -105 -137 -163 -79 -28 27 -50 53
-50 57 0 5 30 43 66 86 79 92 227 313 268 400 33 69 27 68 123 26z m-477 -736
c0 -15 -167 -150 -280 -227 -112 -76 -307 -187 -315 -179 -2 2 -17 33 -34 70
l-29 66 100 57 c142 79 250 153 359 244 l94 79 53 -51 c28 -28 52 -55 52 -59z
m-3072 36 c92 -79 313 -227 400 -268 34 -16 62 -35 62 -42 0 -11 -47 -124 -55
-133 -6 -6 -175 88 -275 153 -93 61 -283 208 -310 241 -12 14 -7 22 35 65 27
28 53 50 57 50 5 0 43 -30 86 -66z m1038 -406 c1 -2 -1 -20 -6 -41 -4 -20 -4
-39 0 -42 4 -3 80 -13 169 -22 l161 -17 0 -79 0 -78 -42 5 c-24 3 -77 8 -118
11 -104 9 -224 30 -361 65 -112 28 -256 76 -272 90 -9 8 42 140 55 140 5 0 55
-16 113 -36 58 -20 111 -34 119 -31 7 3 16 21 20 40 l6 34 76 -18 c42 -10 78
-20 80 -21z m1256 -34 c17 -36 27 -69 22 -73 -12 -11 -211 -76 -309 -100 -111
-28 -261 -51 -382 -59 l-103 -7 0 76 0 76 123 12 c163 16 344 53 486 100 64
22 120 40 124 40 4 1 22 -29 39 -65z"/>
<path d="M1443 4222 c-71 -25 -128 -65 -163 -114 -33 -45 -60 -123 -60 -173 0
-32 -1 -32 -55 -38 -107 -11 -206 -82 -256 -182 -33 -69 -34 -197 -2 -267 69
-151 252 -226 405 -168 l53 20 77 -77 78 -78 0 -394 c0 -270 4 -406 12 -432
14 -50 67 -112 113 -133 20 -10 35 -24 35 -34 0 -10 -71 -88 -158 -175 l-157
-157 -55 21 c-116 44 -266 7 -349 -88 -82 -92 -103 -232 -53 -345 45 -102 170
-188 271 -188 l38 0 6 -54 c8 -76 38 -138 94 -194 151 -150 404 -111 508 79
56 104 42 259 -32 347 l-28 33 -59 -60 c-56 -56 -59 -62 -44 -78 26 -29 38
-88 26 -131 -35 -128 -207 -153 -279 -40 -20 33 -21 84 -3 176 6 28 1 37 -35
73 -36 36 -45 41 -73 35 -91 -18 -143 -17 -175 3 -86 54 -100 165 -31 238 57
59 145 63 209 9 22 -19 42 -26 72 -26 39 0 46 6 193 151 l152 151 61 -80 61
-81 0 -139 c0 -171 7 -195 111 -363 114 -184 199 -258 334 -294 84 -21 466
-21 550 0 132 35 219 109 326 281 111 177 118 202 119 372 l0 143 61 81 61 80
152 -151 c143 -142 155 -151 191 -151 26 0 49 8 72 26 47 36 89 46 137 33 132
-35 159 -207 44 -280 -33 -20 -84 -21 -176 -3 -28 6 -37 1 -73 -35 -38 -38
-41 -44 -35 -78 18 -99 17 -137 -3 -171 -61 -96 -193 -96 -264 -1 -28 39 -27
121 3 161 l22 30 -58 59 c-67 67 -70 67 -120 -24 -26 -47 -29 -61 -29 -147 0
-87 3 -100 30 -149 80 -145 248 -207 402 -150 104 40 188 149 200 262 l6 55
53 4 c77 7 158 51 211 116 129 159 79 399 -104 488 -77 38 -178 44 -253 15
l-55 -21 -157 157 c-87 87 -158 165 -158 175 0 10 15 24 35 34 46 21 99 83
113 133 8 26 12 162 12 432 l0 394 78 78 77 77 53 -20 c153 -58 336 17 405
168 32 70 31 198 -3 267 -49 100 -149 171 -257 182 -52 6 -53 7 -53 38 0 193
-213 346 -405 290 -73 -21 -137 -64 -176 -118 -31 -43 -59 -123 -59 -170 l0
-29 -37 29 c-150 116 -341 190 -558 214 -259 29 -564 -56 -766 -212 l-36 -29
-6 52 c-8 68 -49 149 -94 189 -88 77 -221 107 -320 71z m177 -174 c54 -37 72
-69 72 -128 0 -42 -6 -60 -31 -95 -33 -45 -41 -101 -19 -123 9 -9 2 -31 -29
-94 -23 -46 -49 -110 -58 -143 -9 -33 -18 -66 -21 -74 -3 -9 -24 5 -63 43 -52
49 -65 56 -99 56 -29 0 -49 -7 -71 -26 -42 -35 -86 -46 -135 -33 -132 35 -159
207 -44 280 33 20 84 21 176 3 28 -6 37 -1 73 35 36 36 41 45 35 73 -18 92
-17 143 3 176 45 71 145 95 211 50z m2038 2 c53 -33 74 -76 68 -140 -3 -30 -8
-70 -12 -88 -6 -28 -1 -37 35 -73 36 -36 45 -41 73 -35 91 18 143 17 175 -3
86 -54 100 -165 30 -239 -58 -60 -142 -63 -208 -8 -21 18 -42 26 -69 26 -33 0
-48 -8 -99 -56 -40 -37 -62 -51 -65 -43 -2 8 -14 46 -25 86 -12 39 -37 101
-56 138 -28 52 -33 70 -25 85 18 33 11 81 -16 118 -83 108 -16 252 116 252 27
0 58 -8 78 -20z m-900 -76 c312 -64 559 -279 653 -569 21 -65 23 -91 27 -380
2 -170 2 -328 0 -349 l-3 -40 -36 32 -37 32 -53 -61 -54 -62 82 -76 c98 -92
111 -113 89 -147 -20 -29 -34 -32 -171 -36 -93 -3 -119 -8 -165 -29 -107 -50
-160 -115 -206 -252 -42 -125 -20 -117 -324 -117 -304 0 -282 -8 -324 117 -46
137 -99 202 -206 252 -47 21 -74 26 -183 31 -120 5 -130 7 -148 29 -12 15 -17
31 -13 45 3 12 45 57 92 102 l87 81 -54 62 -54 62 -31 -30 c-18 -17 -35 -31
-40 -31 -4 0 -6 156 -4 348 4 329 5 351 27 417 59 180 170 326 326 430 116 77
209 114 380 149 54 11 272 5 343 -10z m-198 -2609 l405 0 52 27 52 27 -50 -82
c-65 -105 -110 -151 -179 -185 -55 -27 -56 -27 -280 -27 -224 0 -225 0 -280
27 -69 34 -114 80 -179 185 l-50 82 52 -27 52 -27 405 0z"/>
<path d="M1905 3016 c-60 -28 -97 -66 -124 -126 -24 -54 -27 -117 -6 -167 19
-45 114 -164 158 -196 93 -69 226 -60 400 27 113 57 141 97 146 208 4 100 -9
147 -57 200 -63 70 -91 78 -292 78 -163 0 -178 -2 -225 -24z"/>
<path d="M2775 3021 c-51 -23 -111 -89 -126 -139 -6 -21 -10 -75 -8 -120 5
-111 33 -151 146 -208 174 -87 307 -96 400 -27 44 32 139 151 158 196 32 76 5
187 -61 249 -63 59 -102 68 -294 68 -148 0 -181 -3 -215 -19z"/>
<path d="M2524 2634 c-18 -8 -254 -272 -270 -302 -7 -15 -14 -52 -14 -82 0
-111 63 -170 180 -170 45 0 78 6 103 19 36 18 38 18 74 0 47 -24 151 -26 199
-3 47 22 76 67 82 125 8 90 -1 109 -114 236 -145 162 -168 183 -201 182 -16 0
-33 -3 -39 -5z"/>
</g>
</svg>'''

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PDFDecryptor()
    ex.show()
    sys.exit(app.exec_())