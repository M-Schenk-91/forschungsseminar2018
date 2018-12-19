"""
Based on Raphael Wimmer's implementation for the course ITT
See Computational Geometry for Gesture Recognition jupyter notebook
"""

from datastructures.Shape import Shape
from datastructures import Brush
from widgets import QMenuWidget
from style import style
from datastructures.Trackables import *
from datastructures.TrackableTypes import *
from datastructures import Mask
from interaction import Effect

from util.Utility import TaskThread, AnimationThread, InfiniteThread
from interaction import Interaction
from evaluation import Evaluation
from random import randint

import time


class QDrawWidget(QtWidgets.QWidget):
    on_close = QtCore.pyqtSignal()
    on_context_menu_open = QtCore.pyqtSignal(float, float, float, float, int, list)
    on_context_menu_selection = QtCore.pyqtSignal(float, float)
    on_context_menu_close = QtCore.pyqtSignal(float)
    on_new_file_append_requested = QtCore.pyqtSignal(float, float, str, int)
    on_delete_digital_twin = QtCore.pyqtSignal(int)
    on_delete_solo_file = QtCore.pyqtSignal(tuple)
    on_conveyor_move_requested = QtCore.pyqtSignal(float, float, int, list, float, bool)
    on_pd_magnification_requested = QtCore.pyqtSignal(int, float)
    on_file_magnification_requested = QtCore.pyqtSignal(int, float)
    on_shape_deletion = QtCore.pyqtSignal(list)
    on_file_click = QtCore.pyqtSignal(int, int)
    on_thread_visualization_requested = QtCore.pyqtSignal(list, int)
    on_region_move_change_requested = QtCore.pyqtSignal(int, bool, bool)
    on_region_movement_requested = QtCore.pyqtSignal(int, int)
    on_region_collision_deletion = QtCore.pyqtSignal(int)
    on_button_clicked = QtCore.pyqtSignal(int)
    on_evaluation = QtCore.pyqtSignal(dict)
    on_palette_selection = QtCore.pyqtSignal(int)
    on_region_effect_storage_requested = QtCore.pyqtSignal(int, int)
    on_region_effect_transfer_requested = QtCore.pyqtSignal(int, int)
    on_file_effect_transfer_requested = QtCore.pyqtSignal(int, int)

    # only needed for logging as of now
    on_magnification_toggled = QtCore.pyqtSignal(bool, int)
    on_email_delegate_storage_doAtOnce_left = QtCore.pyqtSignal(int)
    on_do_at_once_requested = QtCore.pyqtSignal(list, int, str)
    on_file_drag = QtCore.pyqtSignal(int)

    def __init__(self, app, mp, width=1920, height=1080):
        super().__init__()

        self.DEBUG = False
        self.EVAL_SPECIFICATION_ID = Evaluation.Experiment.ExperimentType.REVIEW.value

        self.app = app
        self.mp = mp

        self.notification_widget = QtWidgets.QLabel()
        self.notification_widget.setWordWrap(True)
        self.notification_widget.setGeometry(self.x() + 20, 1020, int(self.width() / 2), 20)
        self.notification_widget.setText("Current Brush: Region Palette")
        self.notification_widget.fontMetrics().width(self.notification_widget.text())
        self.notification_widget.setMinimumWidth(1920 / 2)

        self.notification_widget.setStyleSheet(style.WidgetStyle.QLABEL_STYLE.value)
        self.notification_widget.setParent(self)

        font = self.notification_widget.font()
        font.setPointSize(14)

        self.notification_widget.setFont(font)
        self.notification_widget.show()

        """
        self.notification_widget2 = QtWidgets.QLabel()
        self.notification_widget2.setGeometry(self.x() + 20, 1050, int(self.width() / 2), 20)
        self.notification_widget2.setText("Current Transfer Effect: None")
        self.notification_widget2.setStyleSheet(style.WidgetStyle.QLABEL_STYLE.value)
        self.notification_widget2.setParent(self)
        self.notification_widget2.setMinimumWidth(1920 / 2)

        font = self.notification_widget2.font()
        font.setPointSize(14)

        self.notification_widget2.setFont(font)
        self.notification_widget2.show()
        """

        self.resize(width, height)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.drawing = False
        self.is_released = False
        self.grid = False
        self.is_logging = False
        self.has_transfer_effect_stored = False
        self.transfer_effect = None
        self.messaged_data = {}
        self.processed_trackables = []
        self.previous_processed_trackables = []
        self.drawn_shapes = []
        self.current_drawn_points = []
        self.setMouseTracking(True)  # do not only get events when button is pressed
        self.current_brush = Brush.Brush(Brush.BrushTypes.NONE.value, None)

        self.current_brush.set_brush_type(Brush.BrushTypes.PALETTE.value)
        self.setCursor(QtCore.Qt.BlankCursor)

        self.shapes_to_assign = []

        #settings = Evaluation.Experiment.get_experiment_specification(self.EVAL_SPECIFICATION_ID)

        settings = None

        if settings is not None:
            self.evaluation_categories = []
            self.pid = -1
            self.apply_evaluation_settings(settings)
            self.eval_csv_path = 'res/eval/review/out/'
            self.last_timestamp = None

            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                self.log_for_experiment('pid', 'timestamp', 'action', 'time_since_last_action', 'file_id', 'categorization_correct', 'categorization_correction')

        else:
            self.file_icons = {
                1: File(1, 50, 50, self, "tasks.txt", """<html><p>hello.txt</p><p>Hello</p></html>""", FileType.TEXT.value, self.DEBUG),
                2: File(2, 105, 50, self, "paper.txt", """<html><div style="margin-top: 15px;"></div><div style="margin-top: 15px;"></div><div><span style="font: 23pt Times New Roman;">Something about HCI</span></div><div style="margin-top: 15px;"></div><div><span style="font: 11pt Times New Roman;">Author 1, Author 2, Author 3</span></div><div style="margin-top: 3px;"></div><div><span style="font: 9pt Times New Roman;">Some Chair at some University</span></div><div style="margin-top: 10px;"></div><div><span style="font: 9pt Times New Roman;"><b>Zusammenfassung</b></span></div><div style="margin-top: 5px;"></div><div><span style="font: 8pt Times New Roman;">In dieser Arbeit wurde auf Basis von Nielsens (1994b) Ten Usability Heuristics in einem recherchebasierten Ansatz anhand von spezifischer Literatur eine domänenspezifische Heuristik für Second-Screen-Anwendungen ausgearbeitet und zu einer Checkliste erweitert. Um die Qualität dieser Checkliste zu bewerten,wurde  eine  heuristische  Evaluation  einer  Second-Screen-Anwendung  mit  fünf  Anwendern durchgeführt und deren Ergebnisse mit einer Nutzerstudie mit 20 Teilnehmern verglichen. Dabei ergab sich  eine  mittlere  Validität  von  0.5  und  eine  hohe  Vollständigkeit  von  0.74.  Das  harmonische  Mittel dieser Werte ergibt bei einer Gleichgewichtung ein F-Maß von 0.6. Dieser Wert spricht für eine ausreichende Validität der erstellten heuristischen Checkliste in der ersten Iteration.</span></div><div style="margin-top: 15px;"></div><div><span style="font: 15pt Times New Roman;">1 Einleitung</span></div><div style="margin-top: 5px;"></div><div><span style="font: 9pt Times New Roman;">Ziel von heuristischen Evaluationen ist die Erfassung des aktuellen Zustands einer Software anhand  von Regeln,  sogenannten  Heuristiken,  mit  dem  Ziel, die Gebrauchstauglichkeit des Untersuchungsobjekts zu verbessern. Dieser Prozess ist iterativ zu sehen, damit die Usability einer  Anwendung  ab  einem  frühem  Entwicklungsstadiums  zunehmend  steigt (Guimaraes  & Martins, 2015, S.46). Heuristische Evaluationen gelten als besonders effiziente  und kosten-günstige Methode zur Bestimmung von Usability-Problemen und orientieren sich oft an den Ten Usability Heuristics von Nielsen(1994b). Um eine möglichst vollständige Liste an Usability-Problemen in einem bestimmten System zu generieren, ist es sinnvoll, ein angepasstes Set an Heuristiken für die jeweilige Domäne zu verwenden (Ling & Salvendy, 2005, S.183). Beispiele hierfür sind Heuristiken für Augmented-Reality-Anwendungen (Guimaraes & Martins, 2015), Information Appliances(Böhm, Schneidermeier & Wolff, 2014) oder Game Design (Pinelle & Wong, 2008). Auch in dem Bereich Second Screen und Smart-TV existieren bereits  Heuristiken (Mosqueira-Rey,  Alonso-Ríos, Prado-Gesto  &  Moret-Bonillo,  2017; Solano  et  al.,  2011) bzw.Guidelines (Pagno,  Costa,  Guedes,  Freitas  &  Nedel,  2015;  Weber, Mayer,  Voit,  Ventura  Fierro  &  Henze,  2016), über die in den jeweiligen Arbeiten allerdings keine Aussage über ihre Validität getroffen wird. Das übergeordnete Ziel von heuristischen Eva-luationen ist eine hohe Validität, mithin die korrekte Vorhersage von schwerwiegenden Usability-Problemen des Untersuchungsgegenstands (Hvannberg, Law & Lárusdóttir, 2007, S.226).Heuristiken  sind  meist  allgemeinformuliert  und  werden  deshalb  von  Anwendern  oft  unterschiedlich interpretiert (Böhm et  al., 2014, S.277). Andere, präzisiere  Heuristiken sind auf-grund ihres Umfangs weniger gut handhabbar. Deshalb wurde für die Heuristiken für Second-Screen-Anwendungen eine Checklisteausgearbeitet, die konkrete und prägnante Anweisungen für  den  Anwender  enthält,  um  eine  effiziente  und  umfassende  Identifikation  von  Usability-Problemen zu ermöglichen (Nielsen & Molich, 1992, 249f.).</span></div></html>""", FileType.TEXT.value, self.DEBUG),
                3: File(3, 160, 50, self, "chi19_logo.png", """res/img/chi2019_logo_final.png""", FileType.IMAGE.value, self.DEBUG),
                4: File(4, 215, 50, self, "DF9081.png", """res/eval/review/img/1.jpg""", FileType.IMAGE.value, self.DEBUG),
                5: File(5, 270, 50, self, "DF9082.png", """res/eval/review/img/2.jpg""", FileType.IMAGE.value, self.DEBUG),
                6: File(6, 225, 50, self, "DF9083.png", """res/eval/review/img/3.jpg""", FileType.IMAGE.value, self.DEBUG),
                7: File(7, 280, 50, self, "DF9084.png", """res/eval/review/img/4.jpg""", FileType.IMAGE.value, self.DEBUG),
                8: File(8, 335, 50, self, "DF9085.png", """res/eval/review/img/5.jpg""", FileType.IMAGE.value, self.DEBUG),
                9: File(9, 390, 50, self, "DF9086.png", """res/eval/review/img/6.jpg""", FileType.IMAGE.value, self.DEBUG),
                10: File(10, 445, 50, self, "DF9087.png", """res/eval/review/img/7.jpg""", FileType.IMAGE.value, self.DEBUG),
                11: File(11, 500, 50, self, "DF9088.png", """res/eval/review/img/8.jpg""", FileType.IMAGE.value, self.DEBUG),
                12: File(12, 555, 50, self, "DF9089.png", """res/eval/review/img/9.jpg""", FileType.IMAGE.value, self.DEBUG)
            }

        self.file_icon_count = len(self.file_icons)

        self.active_menus = []

        self.concurrent_touches = []
        self.concurrent_hands = []

        self.previous_concurrent_touches_1 = []
        self.previous_concurrent_touches_2 = []
        self.previous_concurrent_touches_3 = []
        self.previous_concurrent_touches_4 = []
        self.previous_concurrent_touches_5 = []
        self.previous_concurrent_touches_6 = []
        self.previous_concurrent_touches_7 = []
        self.previous_concurrent_touches_8 = []

        self.previous_concurrent_hands = []

        self.on_context_menu_open.connect(self.show_context_menu)
        self.on_context_menu_selection.connect(self.perform_context_menu_selection)
        self.on_context_menu_close.connect(self.hide_context_menu)
        self.on_new_file_append_requested.connect(self.append_new_file_icon)
        self.on_delete_digital_twin.connect(self.delete_digital_twin_by_physical_id)
        self.on_conveyor_move_requested.connect(self.move_item_on_conveyor_belt)
        self.on_delete_solo_file.connect(self.delete_file)
        self.on_pd_magnification_requested.connect(self.magnify_physical_document)
        self.on_file_magnification_requested.connect(self.magnify_file)
        self.on_shape_deletion.connect(self.delete_regions)
        self.on_file_click.connect(self.click_file)
        self.on_thread_visualization_requested.connect(self.sending_visualization)
        self.on_region_move_change_requested.connect(self.set_region_moveable)
        self.on_region_movement_requested.connect(self.move_region)
        self.on_region_collision_deletion.connect(self.delete_region_by_collision)
        self.on_button_clicked.connect(self.on_button_click)
        self.on_magnification_toggled.connect(self.magnification_toggled)
        self.on_email_delegate_storage_doAtOnce_left.connect(self.pb_regions_left)
        self.on_file_drag.connect(self.file_drag_started)
        self.on_palette_selection.connect(self.on_palette_effect_selected)
        self.on_do_at_once_requested.connect(self.on_do_at_once)
        self.on_region_effect_storage_requested.connect(self.store_region_effect)
        self.on_region_effect_transfer_requested.connect(self.transfer_region_effect)
        self.on_file_effect_transfer_requested.connect(self.transfer_file_effect)

        self.interaction_manager = Interaction.Interaction()

        self.update_thread = InfiniteThread(33.0)
        self.update_thread.update_trigger.connect(self.update_all)
        self.update_thread.start()

        self.threads = {}
        self.num_threads = 0

        self.is_context_menu_open = False

        self.masks = []

        self.initUI()

        self.current_brush.set_effect(Effect.Palette())
        self.previous_palette_selection_index = -1
        self.currently_dragged_file = None

        self.test_p = []

        self.is_tangible_active = False
        self.tangible = None
        self.initial_tangible_collision = False
        self.tangible_effect = None

    # <3 heartbeat of everything <3
    def update_all(self):
        self.previous_processed_trackables = self.processed_trackables
        self.processed_trackables = self.mp.get_tracked_objects()

        for icon in self.file_icons.keys():
            self.processed_trackables.append(self.file_icons[icon])

        self.track_touches(self.processed_trackables)
        self.track_tangible()

        self.interaction_manager.process(self)
        self.update()
        # self.app.processEvents()

        if self.currently_dragged_file is not None:
            k = -1

            for i, w in enumerate(self.findChildren(QtWidgets.QLabel, "file")):
                if self.currently_dragged_file.widget == w:
                    k = i

            if k > -1:
                for n in range(len(self.findChildren(QtWidgets.QLabel, "file")) - k):
                    self.currently_dragged_file.widget.raise_()
                    self.currently_dragged_file.widget.name_widget.raise_()

    def track_tangible(self):
        tangible_index = -1

        for i, t in enumerate(self.processed_trackables):
            if t.type_id == TrackableTypes.TANGIBLE.value:
                tangible_index = i

                break

        if tangible_index > -1:
            if self.processed_trackables[tangible_index].id not in [t.id for t in self.previous_processed_trackables]: # potential problem with PhysDoc
                self.is_tangible_active = True
                self.tangible = self.processed_trackables[tangible_index]
                self.initial_tangible_collision = False
            else:
                self.is_tangible_active = True
                self.tangible = self.processed_trackables[tangible_index]
                self.tangible.set_effect(self.tangible_effect)
        else:
            self.is_tangible_active = False
            self.tangible = None
            self.tangible_effect = None
            self.initial_tangible_collision = False

    def on_do_at_once(self, roi, target_id, tagging):
        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                timestamp = int(time.time() * 1000)

                if self.last_timestamp is None:
                    duration = 'NA'
                else:
                    duration = timestamp - self.last_timestamp

                self.last_timestamp = timestamp

                action = "Entered Tag Region " + tagging

                self.log_for_experiment(self.pid, timestamp, action, duration, target_id, 'NA', 'NA')

    def generate_palette_extension_shapes(self, shape_index, effect_type, data):
        m, temp = smath.Math.palette_circle_extension(self.drawn_shapes[shape_index].roi[1:-1], self.drawn_shapes[self.drawn_shapes[shape_index].palette_parent])

        n = 0

        for i, p in enumerate(self.drawn_shapes[self.drawn_shapes[shape_index].palette_parent].roi):
            if p == m:
                n = i

        k = 0

        temp1 = temp[n:] + temp[:n]
        temp2 = self.drawn_shapes[self.drawn_shapes[shape_index].palette_parent].roi[n:] + self.drawn_shapes[self.drawn_shapes[shape_index].palette_parent].roi[:n]

        upper = []
        lower = []

        upper.append(temp1[0])
        lower.append(temp2[0])

        for i, s in enumerate(temp1[1:]):
            upper.append(s)
            lower.append(temp2[i])

            if i > 0 and i % 8 == 0:
                roi = [upper[0]] + lower + list(reversed(upper))

                self.drawn_shapes.append(Shape())

                self.drawn_shapes[-1].is_palette_extended = True
                self.drawn_shapes[-1].set_effect(Effect.Palette())

                if k < len(data):
                    self.drawn_shapes[-1].set_palette_effect(self.drawn_shapes[shape_index].palette_effect, effect_type, data[k])

                self.drawn_shapes[-1].set_roi(roi)
                self.drawn_shapes[-1].parent = self
                self.drawn_shapes[-1].is_palette_parent = False
                self.drawn_shapes[-1].palette_parent = self.drawn_shapes[shape_index].palette_parent
                self.drawn_shapes[-1].set_image()

                self.masks.append(Mask.Mask(self.drawn_shapes[-1].roi, len(self.drawn_shapes) - 1))

                upper = [s]
                lower = [temp2[i]]

                k += 1

    def on_palette_extension_selected(self, shape_index):
        data = self.drawn_shapes[shape_index].palette_additional_info

        action = ''

        if self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.MAGNIFICATION.value:
            self.current_brush.set_effect(Effect.Magnification([data], False))
            self.current_brush.set_brush_type(Brush.BrushTypes.MAGNIFY.value)
            self.brush_name = "Magnify by {}%".format(str(data) + '%')

            self.notification_widget.setText("Current Brush: Magnification by {0}".format(str(data) + "%"))
            self.notification_widget.fontMetrics().width(self.notification_widget.text())

            if self.is_logging:
                action = "Selected Magnify with factor " + str(data) + '%'

        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.SEND_EMAIL.value:
            self.current_brush.set_effect(Effect.SendMail(data))
            self.current_brush.set_brush_type(Brush.BrushTypes.SEND_MAIL.value)
            self.brush_name = "Send Email To {0}".format(data)

            self.notification_widget.setText("Current Brush: Send Email to {0}".format(data))
            self.notification_widget.fontMetrics().width(self.notification_widget.text())

            if self.is_logging:
                action = "Selected Send_Email with receiver" + str(data)

        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.DELEGATE.value:
            self.current_brush.set_effect(Effect.Delegate(data))
            self.current_brush.set_brush_type(Brush.BrushTypes.DELEGATE.value)
            self.brush_name = "Delegate To {0}".format(data)

            self.notification_widget.setText("Current Brush: Delegate to {0}".format(data))
            self.notification_widget.fontMetrics().width(self.notification_widget.text())

            if self.is_logging:
                action = "Selected Delegate with receiver " + str(data)

        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.TAG.value:
            self.current_brush.set_effect(Effect.Tag(data))
            self.current_brush.set_brush_type(Brush.BrushTypes.TAG.value)
            self.brush_name = "Tag with {0}".format(data)

            self.notification_widget.setText("Current Brush: Tag with {0}".format(data))
            self.notification_widget.fontMetrics().width(self.notification_widget.text())

            if self.is_logging:
                action = "Selected Tag with name: " + str(data)

        self.previous_palette_selection_index = self.drawn_shapes[shape_index].palette_parent

        self.previous_palette_selection_index = self.drawn_shapes[shape_index].palette_parent

        for i in range(len(self.drawn_shapes) - 1, -1, -1):
            if self.drawn_shapes[i].is_palette_extended:
                self.drawn_shapes[i].text.close()
                self.drawn_shapes.pop(i)
                self.masks.pop(i)

        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                timestamp = int(time.time() * 1000)

                if self.last_timestamp is None:
                    duration = 'NA'
                else:
                    duration = timestamp - self.last_timestamp

                self.last_timestamp = timestamp

                self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

    def on_palette_effect_selected(self, shape_index):
        self.drawn_shapes[self.previous_palette_selection_index].palette_effect_selected = False
        self.drawn_shapes[shape_index].palette_effect_selected = True
        self.has_transfer_effect_stored = False
        self.transfer_effect = None

        if not self.drawn_shapes[shape_index].is_palette_extended:
            for i in range(len(self.drawn_shapes) - 1, -1, -1):
                if self.drawn_shapes[i].is_palette_extended:

                    if self.drawn_shapes[i].img is not None:
                        self.drawn_shapes[i].img.close()

                    if self.drawn_shapes[i].text is not None:
                        self.drawn_shapes[i].text.close()

                    self.drawn_shapes.pop(i)
                    self.masks.pop(i)

        if self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.MAGNIFICATION.value:
            if not self.drawn_shapes[shape_index].is_palette_extended:
                magnifying_factors = [15, 25, 50, 75]

                self.generate_palette_extension_shapes(shape_index, Effect.EffectType.MAGNIFICATION.value, magnifying_factors)
            else:
                self.on_palette_extension_selected(shape_index)
                return

        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.DELETION.value:
            self.current_brush.set_effect(Effect.Deletion())
            self.current_brush.set_brush_type(Brush.BrushTypes.DELETION.value)
            self.notification_widget.setText("Current Brush: Region Deletion")
            self.notification_widget.fontMetrics().width(self.notification_widget.text())

            if self.is_logging:
                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                    timestamp = int(time.time() * 1000)

                    if self.last_timestamp is None:
                        duration = 'NA'
                    else:
                        duration = timestamp - self.last_timestamp

                    self.last_timestamp = timestamp

                    action = "Selected Deletion Effect"

                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')
        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.SEND_EMAIL.value:
            if not self.drawn_shapes[shape_index].is_palette_extended:
                receivers = ['Mom', 'Florian', 'Andreas']

                self.generate_palette_extension_shapes(shape_index, Effect.EffectType.SEND_EMAIL.value, receivers)
            else:
                self.on_palette_extension_selected(shape_index)
                return
        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.STORAGE.value:
            self.current_brush.set_effect(Effect.Storage())
            self.current_brush.set_brush_type(Brush.BrushTypes.STORAGE.value)
            self.brush_name = "Storage"
            self.notification_widget.setText("Current Brush: Region Storage")
            self.notification_widget.fontMetrics().width(self.notification_widget.text())

            if self.is_logging:
                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                    timestamp = int(time.time() * 1000)

                    if self.last_timestamp is None:
                        duration = 'NA'
                    else:
                        duration = timestamp - self.last_timestamp

                    self.last_timestamp = timestamp

                    action = "Selected Storage Effect"

                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')
        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.CONVEYOR_BELT.value:
            self.current_brush.set_effect(Effect.ConveyorBelt())
            self.current_brush.set_brush_type(Brush.BrushTypes.CONVEYOR_BELT.value)
            self.brush_name = "Conveyor Belt"
            self.notification_widget.setText("Current Brush: Region Conveyor Belt")
            self.notification_widget.fontMetrics().width(self.notification_widget.text())

            if self.is_logging:
                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                    timestamp = int(time.time() * 1000)

                    if self.last_timestamp is None:
                        duration = 'NA'
                    else:
                        duration = timestamp - self.last_timestamp

                    self.last_timestamp = timestamp

                    action = "Selected Conveyor Belt Effect"

                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')
        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.DELEGATE.value:
            if not self.drawn_shapes[shape_index].is_palette_extended:
                receivers = ['Andreas', 'Lucia', 'Laurin']

                self.generate_palette_extension_shapes(shape_index, Effect.EffectType.DELEGATE.value, receivers)
            else:
                self.on_palette_extension_selected(shape_index)

                return

        elif self.drawn_shapes[shape_index].palette_effect == Effect.EffectType.TAG.value:
            if not self.drawn_shapes[shape_index].is_palette_extended:
                tags = [
                    "Vacation",
                    "Person",
                    "City",
                    "Beach",
                    "Panorama",
                    "Landmark",
                    "Screenshot",
                    "Food",
                    "Selfie",
                    "Pet"
                ]

                self.generate_palette_extension_shapes(shape_index, Effect.EffectType.TAG.value, tags)

            else:
                self.on_palette_extension_selected(shape_index)

                return 

            if self.is_logging:
                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                    timestamp = int(time.time() * 1000)

                    if self.last_timestamp is None:
                        duration = 'NA'
                    else:
                        duration = timestamp - self.last_timestamp

                    self.last_timestamp = timestamp

                    action = "Selected Tag Effect"

                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

        self.previous_palette_selection_index = shape_index

    def store_region_effect(self, touch_id, shape_index):
        self.transfer_effect = self.drawn_shapes[shape_index].effect
        self.has_transfer_effect_stored = True

        # check which kind of effect and store name, values, etc.

        #if self.transfer_effect.effect_type ==

        #self.notification_widget2.setText("Current Transfer Effect: {0}".format()

    def transfer_region_effect(self, touch_id, shape_index):
        if self.drawn_shapes[shape_index].img is not None:
            self.drawn_shapes[shape_index].img.close()

        if self.drawn_shapes[shape_index].text is not None:
            self.drawn_shapes[shape_index].text.setText("")
            self.drawn_shapes[shape_index].text.close()

        self.drawn_shapes[shape_index].effect = self.transfer_effect
        self.drawn_shapes[shape_index].set_image()

    def transfer_file_effect(self, touch_id, file_id):
        if self.transfer_effect.effect_type == Effect.EffectType.DELETION.value:
            self.delete_file(self.file_icons[file_id].center)
        elif self.transfer_effect.effect_type == Effect.EffectType.MAGNIFICATION.value:
            if not self.file_icons[file_id].is_transfer_magnified:
                self.file_icons[file_id].is_transfer_magnified = True
                self.magnify_file(file_id, self.transfer_effect.factor)
            else:
                self.file_icons[file_id].is_transfer_magnified = False
        elif self.transfer_effect.effect_type == Effect.EffectType.TAG.value:
            pass

        # and so on for other effect types

    def magnification_toggled(self, toggle, file_id):
        if toggle:
            action = "Entered Seamless Preview"
        else:
            action = "Left Seamless Preview"

        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                timestamp = int(time.time() * 1000)

                if self.last_timestamp is None:
                    duration = 'NA'
                else:
                    duration = timestamp - self.last_timestamp

                self.last_timestamp = timestamp

                self.log_for_experiment(self.pid, timestamp, action, duration, file_id, 'NA', 'NA')

    def pb_regions_left(self, file_index):
        if len(self.file_icons) > 0:
            if self.is_logging:
                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                    action = ''

                    if self.file_icons[file_index].emailed:
                        action = 'Left Send-via-Email Region'
                    elif self.file_icons[file_index].stored:
                        action = 'Left Storage Region'
                    elif self.file_icons[file_index].delegated:
                        action = 'Left Delegate Region'
                    elif self.file_icons[file_index].done_at_once:
                        action = 'Left Tag Region'

                    if action != '':
                        timestamp = int(time.time() * 1000)

                        if self.last_timestamp is None:
                            duration = 'NA'
                        else:
                            duration = timestamp - self.last_timestamp

                        self.last_timestamp = timestamp

                        self.log_for_experiment(self.pid, timestamp, action, duration, file_index, 'NA', 'NA')

    def file_drag_started(self, _id):
        if self.is_logging and not self.file_icons[_id].grabbed:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                timestamp = int(time.time() * 1000)

                if self.last_timestamp is None:
                    duration = 'NA'
                else:
                    duration = timestamp - self.last_timestamp

                action = 'Dragging of File Started'

                self.last_timestamp = timestamp

                self.log_for_experiment(self.pid, timestamp, action, duration, str(_id), 'NA', 'NA')

    def on_button_click(self, _id):
        self.show_context_menu(self.button.x, self.button.y - 150, 50, 50, _id)

    def set_region_moveable(self, idx, toggle, is_attached):
        if toggle:
            for i in range(len(self.drawn_shapes) - 1, -1, -1):
                if self.drawn_shapes[i].is_palette_extended:
                    self.drawn_shapes[i].text.close()
                    self.drawn_shapes.pop(i)
                    self.masks.pop(i)

        self.drawn_shapes[idx].moveable = toggle
        self.drawn_shapes[idx].attached = is_attached

        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                timestamp = int(time.time() * 1000)

                if self.last_timestamp is None:
                    duration = 'NA'
                else:
                    duration = timestamp - self.last_timestamp

                action = 'Movement of ' + ('None' if self.drawn_shapes[idx].effect is None else self.drawn_shapes[idx].effect.name) + ' Region started'

                self.last_timestamp = timestamp

                self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

    def move_region(self, touch_id, shape_index):
        self.drawing = False
        self.current_drawn_points = []

        for t1 in self.concurrent_touches:
            for t2 in self.previous_concurrent_touches_1:
                if touch_id == t1.id == t2.id:
                    self.drawn_shapes[shape_index].touch_id = touch_id
                    self.drawn_shapes[shape_index].push(t1.center[0] - t2.center[0], t1.center[1] - t2.center[1])

                    if self.drawn_shapes[shape_index].attached:
                        self.masks[shape_index] = Mask.Mask(self.drawn_shapes[shape_index].roi, shape_index)

                    return

    def sending_visualization(self, roi, file_index):
        target_shape_index = -1

        for i in range(len(self.drawn_shapes)):
            if self.drawn_shapes[i].roi == roi:
                target_shape_index = i

        self.num_threads = self.num_threads + 1 if self.num_threads < 1000 else 1

        num = self.num_threads

        self.threads[num] = TaskThread(target_shape_index, self.drawn_shapes[target_shape_index].list_view.item_rows[self.drawn_shapes[target_shape_index].list_view.model().rowCount() - 1], num)
        self.threads[num].update_trigger.connect(self.visualize_progressbar)
        self.threads[num].on_finished.connect(self.stop_visualize_progressbar)

        self.threads[num].start()

        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                timestamp = int(time.time() * 1000)

                if self.last_timestamp is None:
                    duration = 'NA'
                else:
                    duration = timestamp - self.last_timestamp

                self.last_timestamp = timestamp

                action = ''
                correct_category = False

                if self.drawn_shapes[target_shape_index].effect.effect_type == Effect.EffectType.STORAGE.value:
                    action = 'Entered Storage Region'
                elif self.drawn_shapes[target_shape_index].effect.effect_type == Effect.EffectType.DELEGATE.value:
                    action = 'Entered Delegate Region for ' + self.drawn_shapes[target_shape_index].effect.receiver
                    correct_category = self.evaluation_categories[file_index] == 'delegate'
                elif self.drawn_shapes[target_shape_index].effect.effect_type == Effect.EffectType.SEND_EMAIL.value:
                    action = 'Entered Send-via-Email Region for ' + self.drawn_shapes[target_shape_index].effect.receiver
                    correct_category = self.evaluation_categories[file_index] == 'send'

                if action != '':
                    self.log_for_experiment(self.pid, timestamp, action, duration, file_index, correct_category, 'NA')

    def visualize_progressbar(self, progress, target_shape_index, target_shape_list_view_row_index):
        if not self.drawn_shapes[target_shape_index].moveable:
            self.drawn_shapes[target_shape_index].update_progress(progress, target_shape_list_view_row_index)

    def stop_visualize_progressbar(self, target_shape_index, target_shape_list_view_row_index, thread_num):
        if not self.drawn_shapes[target_shape_index].moveable:
            self.threads.pop(thread_num)
            self.drawn_shapes[target_shape_index].remove_completed_item(target_shape_list_view_row_index)

    def track_touches(self, trackables):
        temp = []

        for i in range(len(trackables)):
            if trackables[i].type_id == TrackableTypes.TOUCH.value:
                for k in range(len(self.concurrent_touches)):
                    if trackables[i].id == self.concurrent_touches[k].id:

                        self.concurrent_touches[k].successive_detection_increments += 1

                        trackables[i].successive_detection_increments = self.concurrent_touches[k].successive_detection_increments
                        break

                temp.append(trackables[i])

        for k, f in self.file_icons.items():
            if f.touch_id not in [i.id for i in self.concurrent_touches]:
                self.currently_dragged_file = None

                if self.is_logging and f.grabbed:
                    if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                        timestamp = int(time.time() * 1000)

                        if self.last_timestamp is None:
                            duration = 'NA'
                        else:
                            duration = timestamp - self.last_timestamp

                        action = 'Dragging of File Stopped'

                        self.last_timestamp = timestamp

                        self.log_for_experiment(self.pid, timestamp, action, duration, str(f.id), 'NA', 'NA')

                f.grabbed = False
                f.conveyable = True

        self.previous_concurrent_touches_8 = self.previous_concurrent_touches_7
        self.previous_concurrent_touches_7 = self.previous_concurrent_touches_6
        self.previous_concurrent_touches_6 = self.previous_concurrent_touches_5
        self.previous_concurrent_touches_5 = self.previous_concurrent_touches_4
        self.previous_concurrent_touches_4 = self.previous_concurrent_touches_3
        self.previous_concurrent_touches_3 = self.previous_concurrent_touches_2
        self.previous_concurrent_touches_2 = self.previous_concurrent_touches_1
        self.previous_concurrent_touches_1 = self.concurrent_touches
        self.concurrent_touches = temp

        for pct in self.previous_concurrent_touches_1 \
                   + self.previous_concurrent_touches_2 \
                   + self.previous_concurrent_touches_3 \
                   + self.previous_concurrent_touches_4 \
                   + self.previous_concurrent_touches_5\
                   + self.previous_concurrent_touches_6 \
                   + self.previous_concurrent_touches_7 \
                   + self.previous_concurrent_touches_8:

            last_ct_id = -1

            for ct in self.concurrent_touches:
                if pct.id != ct.id and last_ct_id != pct.id:
                    v = (ct.position[0] - pct.position[0], ct.position[1] - pct.position[1])

                    distance = smath.Math.vector_norm(v)

                    if distance < 350:
                        ct.id = pct.id
                        last_ct_id = ct.id

                        break

        for pct in self.previous_concurrent_touches_1:
            if pct.id not in [i.id for i in self.concurrent_touches]:
                self.app.postEvent(self, QtGui.QMouseEvent(QtGui.QMouseEvent.MouseButtonRelease, QtCore.QPoint(pct.position[0], pct.position[1]), QtCore.Qt.LeftButton, QtCore.Qt.NoButton, QtCore.Qt.NoModifier))

        for ct in self.concurrent_touches:
            self.cursor().setPos(self.mapToGlobal(QtCore.QPoint(ct.position[0], ct.position[1])))

            for roi in [self.file_icons[f].roi for f in self.file_icons.keys()]:
                if smath.Math.aabb_in_aabb(Shape(ct.roi).aabb, Shape(roi).aabb):
                    return

            if ct.is_holding():
                self.app.postEvent(self, QtGui.QMouseEvent(QtGui.QMouseEvent.MouseMove, QtCore.QPoint(ct.position[0], ct.position[1]), QtCore.Qt.LeftButton, QtCore.Qt.NoButton, QtCore.Qt.NoModifier))
            elif ct.id not in [i.id for i in self.previous_concurrent_touches_1]:
                self.app.postEvent(self, QtGui.QMouseEvent(QtGui.QMouseEvent.MouseButtonPress, QtCore.QPoint(ct.position[0], ct.position[1]), QtCore.Qt.LeftButton, QtCore.Qt.NoButton, QtCore.Qt.NoModifier))

        for i, s in enumerate(self.drawn_shapes):
            if s.touch_id != -1:
                if s.touch_id not in [ct.id for ct in self.concurrent_touches]:
                    self.drawn_shapes[i].touch_id = -1
                    self.drawn_shapes[i].moveable = False
                    self.drawn_shapes[i].attached = False
                    self.drawn_shapes[i].dropped = True

                    self.masks[i] = Mask.Mask(self.drawn_shapes[i].roi, i)

                    if self.drawn_shapes[i].effect.effect_type == Effect.EffectType.PALETTE.value:
                        for k in self.drawn_shapes[i].palette_children_indices:
                            self.drawn_shapes[k].touch_id = -1
                            self.drawn_shapes[k].moveable = False
                            self.drawn_shapes[k].attached = False
                            self.drawn_shapes[k].dropped = True

                            self.masks[k] = Mask.Mask(self.drawn_shapes[k].roi, k)

                    if self.is_logging:
                        if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                            timestamp = int(time.time() * 1000)

                            if self.last_timestamp is None:
                                duration = 'NA'
                            else:
                                duration = timestamp - self.last_timestamp

                            action = 'Movement of ' + ('None' if self.drawn_shapes[i].effect is None else self.drawn_shapes[i].effect.name) + ' Region stopped'

                            self.last_timestamp = timestamp

                            self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

    def track_hands(self, trackables, target_widget):
        temp = []

        for i in range(len(trackables)):
            if trackables[i].type_id == TrackableTypes.HAND.value:
                temp.append(trackables[i])

        self.previous_concurrent_hands = self.concurrent_hands
        self.concurrent_hands = temp

    def show_context_menu(self, x, y, width, height, _id, shapes=[]):
        self.drawing = False

        action = ''

        if not self.is_context_menu_open:
            k = -1

            if len(shapes) > 0:
                for i in range(len(self.drawn_shapes)):
                    k += 1

                    if shapes[0].roi == self.drawn_shapes[i].roi:
                        break

            self.is_context_menu_open = True

            if k > -1:
                if not self.drawn_shapes[k].is_active:
                    menu = QMenuWidget.QMenuWidget(x, y, width, height, _id, self, self.drawn_shapes[k])
                    menu.add_top_level_menu()

                    self.active_menus.append(menu)
                    self.active_menus[-1].show()

                    if self.is_logging:
                        if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                            action = 'Context Menu Requested for Region Reassignment'
            else:
                menu = QMenuWidget.QMenuWidget(x, y, width, height, _id, self)
                menu.add_top_level_menu()

                self.active_menus.append(menu)
                self.active_menus[-1].show()

                if self.is_logging:
                    if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                        action = 'Context Menu Requested for Brush Assignment'

        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value and action is not '':

                pid = self.pid
                timestamp = int(time.time() * 1000)

                if self.last_timestamp is None:
                    duration = 'NA'
                else:
                    duration = timestamp - self.last_timestamp

                self.last_timestamp = timestamp

                self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

    def hide_context_menu(self, id_to_close):
        self.drawing = False

        caller_ids = [i.caller_id for i in self.active_menus]

        idx = -1

        for i in range(len(caller_ids)):
            caller_id = caller_ids[i]

            if id_to_close == caller_id:
                if self.active_menus[i].sub_menu is not None:
                    self.active_menus[i].sub_menu.close()

                self.active_menus[i].close()

                idx = i

        if idx != -1:
            self.is_context_menu_open = False
            self.active_menus.pop(idx)

    def perform_context_menu_selection(self, x, y):
        self.drawing = False

        self.cursor().setPos(self.mapToGlobal(QtCore.QPoint(x, y)))

        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                performed_action = ''

        for menu in self.active_menus:
            action = menu.activeAction()

            if action is not None:
                action.trigger()

                if self.is_logging:
                    if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                        performed_action = "Selected " + action.text()[1:]

                menu.close()

            sub_menu = menu.sub_menu

            if sub_menu is not None:
                sub_menu_action = sub_menu.activeAction()

                if sub_menu_action is not None:
                    if self.is_logging:
                        if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                            performed_action += ("with " + sub_menu_action.text()[1:])

                    sub_menu_action.trigger()
                    sub_menu.close()

        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value and performed_action != '':

                timestamp = int(time.time() * 1000)

                if self.last_timestamp is None:
                    duration = 'NA'
                else:
                    duration = timestamp - self.last_timestamp

                self.last_timestamp = timestamp

                self.log_for_experiment(self.pid, timestamp, performed_action, duration, 'NA', 'NA', 'NA')

    def delete_file(self, center):
        idx = -1

        for key in self.file_icons.keys():
            if center == self.file_icons[key].center:
                idx = key
                self.file_icons[key].clear()
                break

        if idx != -1:
            self.file_icons.pop(idx, None)

            if self.is_logging:
                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                    timestamp = int(time.time() * 1000)
                    action = 'Deletion of File'
                    if self.last_timestamp is None:
                        duration = 'NA'
                    else:
                        duration = timestamp - self.last_timestamp
                    self.last_timestamp = timestamp
                    file_id = idx
                    categorization = self.evaluation_categories[idx] == 'delete'
                    self.log_for_experiment(self.pid, timestamp, action, duration, str(file_id), str(categorization), 'NA')

    def append_new_file_icon(self, x, y, name, physical_representation_id):
        if physical_representation_id not in [self.file_icons[i].physical_representation_id for i in self.file_icons.keys()]:

            self.file_icon_count = self.file_icon_count + 1 if self.file_icon_count < 1000 else 1

            if physical_representation_id == 1:
                self.file_icons[self.file_icon_count] = File(self.file_icon_count, x, y, self, name, """""" + str(name) + "\n-------------------"
                                                                                                                          """The ACM Conference on Human Factors in Computing Systems (CHI) series of academic conferences is generally considered the most prestigious in the field of human–computer interaction and is one of the top ranked conferences in computer science.[1] It is hosted by ACM SIGCHI, the Special Interest Group on computer–human interaction. CHI has been held annually since 1982 and attracts thousands of...""", FileType.TEXT.value, True, physical_representation_id, self.DEBUG)
                self.file_icons[self.file_icon_count].widget.show()
                self.file_icons[self.file_icon_count].stored = True
                self.file_icons[self.file_icon_count].magnified = True
                self.file_icons[self.file_icon_count].emailed = True
                self.file_icons[self.file_icon_count].delegated = True
            elif physical_representation_id == 0:
                self.file_icons[self.file_icon_count] = File(self.file_icon_count, x, y, self, name, "res/img/file_icon.png", FileType.IMAGE.value, True, physical_representation_id, self.DEBUG)

                self.file_icons[self.file_icon_count].widget.show()
                self.file_icons[self.file_icon_count].stored = True
                self.file_icons[self.file_icon_count].magnified = True
                self.file_icons[self.file_icon_count].emailed = True
                self.file_icons[self.file_icon_count].delegated = True

    def delete_digital_twin_by_physical_id(self, _id):
        idx = -1

        for key in self.file_icons.keys():
            p = self.file_icons[key]

            if p.type_id == TrackableTypes.FILE.value:
                if p.physical_representation_id == _id:
                    idx = key
                    break

        if idx > -1:
            self.file_icons[idx].set_digital_twin(-1)
            self.file_icons[idx].clear()
            self.file_icons.pop(idx, None)

    def move_item_on_conveyor_belt(self, x1, y1, idx, full_path, animation_time, looped):
        for key in self.file_icons.keys():
            if not self.file_icons[key].grabbed:
                if not self.file_icons[key].is_on_conveyor_belt:
                    if self.file_icons[key].center[0] == x1 and self.file_icons[key].center[1] == y1:
                        self.file_icons[key].is_on_conveyor_belt = True

                        if len(full_path[idx:]) > 1:
                            if not looped:
                                p, q = full_path[idx:][-1], full_path[idx:][-2]

                                v = smath.Math.normalize_vector((p[0] - q[0], p[1] - q[1]))
                            else:
                                p, q = full_path[idx:][0], full_path[idx:][-1]

                                v = smath.Math.normalize_vector((p[0] - q[0], p[1] - q[1]))

                            v[0] *= 50
                            v[1] *= 50

                            if self.file_icons[key].anim_id == -1:
                                self.animate(key, idx, full_path, animation_time, v, looped)

                                if self.is_logging:
                                    timestamp = int(time.time() * 1000)
                                    action = 'Entered Conveyor Belt'
                                    if self.last_timestamp is None:
                                        duration = 'NA'
                                    else:
                                        duration = timestamp - self.last_timestamp

                                    self.last_timestamp = timestamp

                                    self.log_for_experiment(self.pid, timestamp, action, duration, self.file_icons[key].id, 'NA', 'NA')
            else:
                if self.file_icons[key].anim_id != -1:
                    if self.file_icons[key].anim_id in self.threads.keys():
                        self.threads[self.file_icons[key].anim_id].on_stop()

                    self.file_icons[key].anim_id = -1

                    if self.is_logging:
                        if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                            timestamp = int(time.time() * 1000)
                            action = 'Exited Conveyor Belt via User'
                            if self.last_timestamp is None:
                                duration = 'NA'
                            else:
                                duration = timestamp - self.last_timestamp

                            self.last_timestamp = timestamp

                            self.log_for_experiment(self.pid, timestamp, action, duration, key, 'NA', 'NA')

    def animate(self, idx, path_index, full_path, animation_time, v, looped):
        num_thread = self.num_threads = self.num_threads + 1 if self.num_threads < 1000 else 1

        self.file_icons[idx].anim_id = num_thread

        self.threads[num_thread] = AnimationThread(idx, num_thread, self.file_icons[idx].widget, path_index, full_path, animation_time, v, looped)
        self.threads[num_thread].animation_start.connect(self.on_animation_requested)
        self.threads[num_thread].update_trigger.connect(self.on_animation_update)
        self.threads[num_thread].on_finished.connect(self.on_animation_stop_requested)

        self.threads[num_thread].start()

    def on_animation_requested(self, animation):
        animation.start()

    def on_animation_update(self):
        self.app.processEvents()

    def on_animation_stop_requested(self, thread_num, file_index):
        self.threads.pop(thread_num)

        if self.is_logging:
            if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                timestamp = int(time.time() * 1000)

                if timestamp - self.last_timestamp > 30:  # one frame
                    action = 'Exited Conveyor Belt via Ending'
                    if self.last_timestamp is None:
                        duration = 'NA'
                    else:
                        duration = timestamp - self.last_timestamp

                    self.last_timestamp = timestamp

                    self.log_for_experiment(self.pid, timestamp, action, duration, str(file_index), 'NA', 'NA')

    def magnify_physical_document(self, _id, factor):
        for t in self.processed_trackables:
            if t.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
                if t.id == _id:
                    pass

    def magnify_file(self, _id, factor):
        self.file_icons[_id].show_preview()

    def delete_regions(self, region):
        if region[0] is not None:
            for i in range(len(self.drawn_shapes) - 1, -1, -1):
                if region[0].roi == self.drawn_shapes[i].roi:
                    self.drawn_shapes[i].set_roi([])

                    if self.drawn_shapes[i].img is not None:
                        self.drawn_shapes[i].img.close()

                    if self.drawn_shapes[i].text is not None:
                        self.drawn_shapes[i].text.setText('')
                        self.drawn_shapes[i].text.close()

                    if self.is_logging:
                        if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                            timestamp = int(time.time() * 1000)

                            if self.last_timestamp is None:
                                duration = 'NA'
                            else:
                                duration = timestamp - self.last_timestamp

                            self.last_timestamp = timestamp

                            action = 'Deletion of ' + ('None' if self.drawn_shapes[i].effect is None else self.drawn_shapes[i].effect.name)

                            self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

                    self.drawn_shapes.pop(i)
                    self.masks.pop(i)

                    if self.previous_palette_selection_index > i:
                        self.previous_palette_selection_index -= 1

    def delete_region_by_collision(self, region_index):
        self.delete_regions([self.drawn_shapes[region_index]])

    def click_file(self, _id, touch_id):
        for k, f in self.file_icons.items():
            if f.id == _id:
                f.grabbed = True

    def initUI(self):
        self.setWindowTitle('Canvas')

        if not self.DEBUG:
            self.showFullScreen()

        for icon in self.file_icons.keys():
            self.file_icons[icon].widget.setParent(self)
            self.file_icons[icon].widget.show()

        self.show()

        # self.__create_default_delete_region()

    def apply_evaluation_settings(self, settings):
        self.is_logging = True
        self.file_icons = {}

        for d in settings:
            _id = d['id']
            content = d['content']

            self.evaluation_categories.append(d['category'])
            self.file_icons[_id] = File(_id, 1920 / 2 + randint(0, 50), 800 + randint(0, 50), self, "DF0A8" + str(_id) + ".jpg", content, FileType.TEXT.value if content[0] != 'r' else FileType.IMAGE.value, self.DEBUG)

        self.pid = settings[0]['pid']

    def log_for_experiment(self, *args):
        Evaluation.Experiment.Logging.log(self.eval_csv_path + "review_p_" + str(self.pid) + '.csv', list(args))

    def __create_default_delete_region(self):
        self.drawn_shapes.append(Shape(effect=Effect.Deletion()))

        self.drawn_shapes[-1].set_roi([(1650, 760), (1650, 1060), (1900, 1060), (1900, 760)])
        self.drawn_shapes[-1].set_effect(Effect.Deletion())
        self.drawn_shapes[-1].parent = self
        self.drawn_shapes[-1].set_image()

        self.masks.append(Mask.Mask(self.drawn_shapes[-1].roi, len(self.drawn_shapes) - 1))

    def get_file_dictionary(self):
        return self.file_icons

    def get_drawn_shapes(self):
        return self.drawn_shapes

    def is_over_icon(self):
        for icon in self.file_icons:
            if self.file_icons[icon].widget.is_over_icon:
                return True

        return False

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_Return:
            self.handle_return_key()
        elif ev.key() == QtCore.Qt.Key_Delete:
            self.handle_delete_key()

            for key, value in self.animations.items():
                value.pause()
                value.stop()

            for f in self.file_icons.keys():
                self.file_icons[f].is_on_conveyor_belt = False

        elif ev.key() == QtCore.Qt.Key_Q or ev.key() == QtCore.Qt.Key_Escape:
            self.handle_exit_key()

    def handle_return_key(self):
        pass

    def handle_exit_key(self):
        self.close()
        self.on_close.emit()

    def handle_delete_key(self):
        for s in self.drawn_shapes:
            if s.img is not None:
                s.img.setPixmap(QtGui.QPixmap())
                s.img.close()

            if s.text is not None:
                s.text.close()

            if s.effect is not None:
                if s.effect.effect_type == Effect.EffectType.SEND_EMAIL.value:
                    if s.progress is not None:
                        s.progress.close()

                    if s.sending_text is not None:
                        s.sending_text.setText("")
                        s.sending_text.close()

        self.drawn_shapes = []
        self.current_drawn_points = []

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton and not self.is_over_icon():
            self.is_released = False
            self.drawing = True

            for s in self.drawn_shapes:
                s.dropped = False

            self.current_drawn_points = []

            if self.is_logging and len(self.active_menus) == 0:
                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                    timestamp = int(time.time() * 1000)

                    action = 'Started Drawing'

                    if self.last_timestamp is None:
                        duration = 'NA'
                    else:
                        duration = timestamp - self.last_timestamp

                    self.last_timestamp = timestamp

                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

    def mouseReleaseEvent(self, ev):
        if ev.button() == QtCore.Qt.LeftButton:
            if not self.is_over_icon():

                self.drawing = False
                self.is_released = True

                if len(self.current_drawn_points) > 0:
                    if self.is_logging:
                        if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                            timestamp = int(time.time() * 1000)

                            action = 'Stopped Drawing'

                            if self.last_timestamp is None:
                                duration = 'NA'
                            else:
                                duration = timestamp - self.last_timestamp

                            self.last_timestamp = timestamp

                            self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

                    self.drawn_shapes.append(Shape(effect=self.current_brush.get_effect(), parent=self))

                    if self.current_brush.effect is None:
                        self.brush_name = "None"
                    else:
                        self.brush_name = self.current_brush.effect.name

                    if self.current_brush.brush_tpye != Brush.BrushTypes.CONVEYOR_BELT.value:
                        if smath.Math.sufficient_shape_area(self.current_drawn_points):
                            self.current_drawn_points.append(self.current_drawn_points[0])

                            self.drawn_shapes[-1].set_roi(self.current_drawn_points)
                            self.drawn_shapes[-1].set_effect(self.current_brush.get_effect())
                            self.drawn_shapes[-1].parent = self
                            self.drawn_shapes[-1].is_palette_parent = False

                            self.masks.append(Mask.Mask(self.drawn_shapes[-1].roi, len(self.drawn_shapes) - 1))

                            if self.current_brush.get_brush_type() == Brush.BrushTypes.PALETTE.value:
                                radius = int(sum(smath.Math.vector_norm((p[0] - self.drawn_shapes[-1].center[0], p[1] - self.drawn_shapes[-1].center[1])) for p in self.drawn_shapes[-1].roi) / len(self.drawn_shapes[-1].roi))

                                new_roi = smath.Math.compute_circle(self.drawn_shapes[-1].center[0], self.drawn_shapes[-1].center[1], radius)
                                self.drawn_shapes[-1].is_palette_parent = True

                                self.drawn_shapes[-1].set_roi(smath.Math.resample_points(new_roi, 84))

                                parent_shape_index = len(self.drawn_shapes) - 1

                                for i, roi in enumerate(self.drawn_shapes[parent_shape_index].sub_area_rois):
                                    self.drawn_shapes.append(Shape())
                                    self.drawn_shapes[-1].set_effect(self.current_brush.get_effect())
                                    self.drawn_shapes[-1].set_palette_effect(i + 1)
                                    self.drawn_shapes[-1].set_roi(roi)
                                    self.drawn_shapes[-1].parent = self
                                    self.drawn_shapes[-1].is_palette_parent = False
                                    self.drawn_shapes[-1].palette_parent = parent_shape_index
                                    self.drawn_shapes[-1].set_image()
                                    self.drawn_shapes[parent_shape_index].palette_children_indices.append(len(self.drawn_shapes) - 1)

                                    self.masks.append(Mask.Mask(self.drawn_shapes[-1].roi, len(self.drawn_shapes) - 1))

                            if self.is_logging:
                                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                                    timestamp = int(time.time() * 1000)

                                    action = ""

                                    if self.drawn_shapes[-1].effect is None:
                                        action = "None"
                                    else:
                                        action = self.drawn_shapes[-1].effect.name

                                        if self.drawn_shapes[-1].effect.effect_type == Effect.EffectType.TAG.value:
                                            action += " with " + self.drawn_shapes[-1].effect.effect_text
                                        if self.drawn_shapes[-1].effect.effect_type == Effect.EffectType.DELEGATE.value:
                                            action += " " + self.drawn_shapes[-1].effect.effect_text
                                        if self.drawn_shapes[-1].effect.effect_type == Effect.EffectType.SEND_EMAIL.value:
                                            action += " " + self.drawn_shapes[-1].effect.effect_text
                                        if self.drawn_shapes[-1].effect.effect_type == Effect.EffectType.MAGNIFICATION.value:
                                            action += " with " + self.drawn_shapes[-1].effect.effect_text

                                    action += ' Region Drawn Successfully'

                                    if self.last_timestamp is None:
                                        duration = 'NA'
                                    else:
                                        duration = timestamp - self.last_timestamp

                                    self.last_timestamp = timestamp

                                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')
                        else:
                            if self.is_logging:
                                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                                    timestamp = int(time.time() * 1000)

                                    action = ("None" if self.drawn_shapes[-1].effect is None else self.drawn_shapes[-1].effect.name) + ' Region was rejected because of its size'
                                    if self.last_timestamp is None:
                                        duration = 'NA'
                                    else:
                                        duration = timestamp - self.last_timestamp

                                    self.last_timestamp = timestamp

                                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

                            self.drawn_shapes.pop(-1)
                    else:
                        if smath.Math.sufficient_shape_area(self.current_drawn_points, 1000):
                            v = (self.current_drawn_points[0][0] - self.current_drawn_points[-1][0], self.current_drawn_points[0][1] - self.current_drawn_points[-1][1])

                            looped = False

                            if smath.Math.vector_norm(v) < 75:
                                self.current_drawn_points.append(self.current_drawn_points[0])
                                looped = True
                            self.drawn_shapes[-1].set_middle_line(self.current_drawn_points)

                            shape, shape_part_one, shape_part_two = smath.Math.shapify(self.drawn_shapes[-1].middle_line)

                            self.drawn_shapes[-1].shape_part_one = shape_part_one
                            self.drawn_shapes[-1].shape_part_two = shape_part_two
                            self.drawn_shapes[-1].set_roi(shape)
                            self.drawn_shapes[-1].set_effect(self.current_brush.get_effect())
                            self.drawn_shapes[-1].effect.looped = looped
                            self.drawn_shapes[-1].is_looped = looped
                            self.drawn_shapes[-1].parent = self
                            self.drawn_shapes[-1].set_image()
                            self.masks.append(Mask.Mask(self.drawn_shapes[-1].roi, len(self.drawn_shapes) - 1))

                            if self.is_logging:
                                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                                    timestamp = int(time.time() * 1000)

                                    action = ("None" if self.drawn_shapes[-1].effect is None else self.drawn_shapes[-1].effect.name) + ' Shape Drawn Successfully'
                                    if self.last_timestamp is None:
                                        duration = 'NA'
                                    else:
                                        duration = timestamp - self.last_timestamp

                                    self.last_timestamp = timestamp

                                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')
                        else:
                            if self.is_logging:
                                if self.EVAL_SPECIFICATION_ID == Evaluation.Experiment.ExperimentType.REVIEW.value:
                                    timestamp = int(time.time() * 1000)

                                    action = ("None" if self.drawn_shapes[-1].effect is None else self.drawn_shapes[-1].effect.name) + ' Region was rejected because of its size'
                                    if self.last_timestamp is None:
                                        duration = 'NA'
                                    else:
                                        duration = timestamp - self.last_timestamp

                                    self.last_timestamp = timestamp

                                    self.log_for_experiment(self.pid, timestamp, action, duration, 'NA', 'NA', 'NA')

                            self.drawn_shapes.pop(-1)

                if len(self.drawn_shapes) > 0:
                    for w in (self.findChildren(QtWidgets.QLabel, "shape_img") + self.findChildren(QtWidgets.QLabel, "shape_text")):
                        w.lower()

                self.current_drawn_points = []

    def mouseMoveEvent(self, ev):
        if self.drawing:
            self.current_drawn_points.append((ev.x(), ev.y()))

    def poly(self, pts):
        return QtGui.QPolygonF(map(lambda p: QtCore.QPointF(*p), pts))

    def paintEvent(self, ev):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setBrush(QtGui.QColor(0, 0, 0))
        qp.drawRect(ev.rect())
        qp.setBrush(QtGui.QColor(20, 255, 190))

        if self.current_brush.effect is not None:
            if self.current_brush.effect.effect_color is not None:
                qp.setPen(QtGui.QPen(self.current_brush.effect.effect_color, 5))
            else:
                qp.setPen(QtGui.QPen(QtGui.QColor(0, 155, 0), 5))
        else:
            qp.setPen(QtGui.QPen(QtGui.QColor(0, 155, 0), 5))

        qp.drawPolyline(self.poly(self.current_drawn_points))

        for i, t in enumerate(self.processed_trackables):
            if t.type_id == TrackableTypes.TOUCH.value:
                qp.drawEllipse(t.center[0] - 8, t.center[1] - 8, 16, 16)

        for p in self.test_p:
            qp.drawEllipse(p[0] - 7.5, p[1] - 7.5, 15, 15)

        for index, shape in enumerate(self.drawn_shapes):
            path = QtGui.QPainterPath()

            if shape.effect is None:
                qp.drawPolyline(self.poly(shape.roi))

            if len(shape.roi) > 0:
                first_point = shape.roi[0]
                path.moveTo(first_point[0], first_point[1])

            i = 0

            for point in shape.roi:
                if i > 0:
                    path.lineTo(point[0], point[1])

                i += 1

            if len(shape.roi) > 0:
                path.lineTo(first_point[0], first_point[1])

            if shape.moveable:
                for arrow in shape.moveable_highlighting:
                    qp.drawPolyline(self.poly(arrow['upper']))
                    qp.drawPolyline(self.poly(arrow['lower']))
                    qp.drawPolyline(self.poly(arrow['angle_one']))
                    qp.drawPolyline(self.poly(arrow['angle_two']))

            if shape.effect is not None:
                if shape.effect.effect_type is not Effect.EffectType.CONVEYOR_BELT.value and shape.effect.effect_type is not Effect.EffectType.PALETTE.value:
                    qp.fillPath(path, shape.effect.effect_color)
                elif shape.effect.effect_type is Effect.EffectType.PALETTE.value:
                    qp.setPen(QtGui.QPen(QtGui.QColor(0, 155, 0), 5))

                    if not shape.palette_parent:
                        qp.drawPolyline(self.poly(shape.roi))

                        if shape.palette_effect_selected:
                            qp.fillPath(path, shape.effect.effect_colors[shape.effect_color_index])
                        else:
                            qp.fillPath(path, QtGui.QColor("#000000"))
                else:
                    if len(shape.middle_line) > 0:
                        if not shape.is_looped:
                            qp.drawPolyline(self.poly(shape.roi))
                        else:
                            qp.drawPolyline(self.poly(shape.shape_part_one))
                            qp.drawPolyline(self.poly(shape.shape_part_two))

                        for arrow in shape.direction_visualization_arrows:
                            qp.drawPolyline(self.poly(arrow['arrow_part1']))
                            qp.drawPolyline(self.poly(arrow['arrow_part2']))
                            qp.drawPolyline(self.poly(arrow['arrow_base']))

        for i, t in enumerate(self.processed_trackables):
            if t.type_id == TrackableTypes.FILE.value:
                if t.is_digital_twin:
                    for k, p in enumerate(self.processed_trackables):
                        if i == k:
                            continue

                        if p.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
                            if t.physical_representation_id == p.id:
                                qp.drawLine(t.center[0], t.center[1], p.center[0], p.center[1])

                if t.grabbed:
                    qp.drawPolyline(self.poly(t.roi + [t.roi[0]]))

            if t.type_id == TrackableTypes.TANGIBLE.value:
                if self.tangible.effect is None:
                    pass
                    # qp.drawPolyline(self.poly(t.roi))
                else:
                    path = QtGui.QPainterPath()

                    if len(t.roi) > 0:
                        first_point = t.roi[0]
                        path.moveTo(first_point[0], first_point[1])

                    i = 0

                    for point in t.roi:
                        if i > 0:
                            path.lineTo(point[0], point[1])

                        i += 1

                    if len(t.roi) > 0:
                        path.lineTo(first_point[0], first_point[1])

                    if self.tangible.effect is not None:
                        if self.tangible.effect.effect_color is not None:
                            qp.fillPath(path, self.tangible.effect.effect_color)

        if self.DEBUG:
            if len(self.processed_trackables) > 0:
                qp.setPen(QtGui.QColor(0, 255, 0))

                for trackable in self.processed_trackables:
                    if trackable.type_id == TrackableTypes.FILE.value:
                        tlc, blc, brc, trc = trackable.collision_roi[0], trackable.collision_roi[1], trackable.collision_roi[2], trackable.collision_roi[3]
                    else:
                        tlc, blc, brc, trc = trackable.roi[0], trackable.roi[1], trackable.roi[2], trackable.roi[3]

                    center = trackable.center

                    qp.drawLine(tlc[0], tlc[1], trc[0], trc[1])
                    qp.drawLine(tlc[0], tlc[1], blc[0], blc[1])
                    qp.drawLine(blc[0], blc[1], brc[0], brc[1])
                    qp.drawLine(trc[0], trc[1], brc[0], brc[1])

                    qp.drawEllipse(center[0] - 7.5, center[1] - 7.5, 15, 15)

        if len(self.processed_trackables) > 0:
            qp.setPen(QtGui.QPen(QtGui.QColor(0, 155, 0), 5))

            for trackable in self.processed_trackables:
                if trackable.type_id == TrackableTypes.FILE.value:
                    if trackable.is_digital_twin:
                        for p in self.processed_trackables:
                            if p.type_id == TrackableTypes.PHYSICAL_DOCUMENT.value:
                                if trackable.physical_representation_id == p.id:
                                    qp.drawLine(trackable.center[0], trackable.center[1], p.center[0], p.center[1])
        qp.end()
