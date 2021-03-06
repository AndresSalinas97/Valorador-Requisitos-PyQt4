#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo con el controlador del valorador.

Autor: Andrés Salinas Lima <i52salia@uco.es>.
"""

from __future__ import print_function
from valorador_view import ValoradorMessageBoxes
import sys
from PyQt4 import QtGui


class ValoradorController():
    """
    Clase con el controlador del valorador.

    Argumentos constructor:
        model: Objeto de la clase ValoradorModel.
        view: Objeto de la clase ValoradorView.
    """

    def __init__(self, model, view):
        self._model = model
        self._view = view

        self._caso = self._model.caso
        self._main_widget = self._view.main_widget
        self._main_window = self._view.main_window

        self._init_model()
        self._init_view()
        self._init_controller()

    def _init_model(self):
        """
        Inicializa el modelo.
        """
        pass

    def _init_view(self):
        """
        Inicializa la vista.
        """
        self._update_entire_UI()
        self._view.show()

    def _init_controller(self):
        """
        Inicializa el controlador.

        Conecta los botones y acciones de la vista con métodos del controlador.
        """
        self._main_widget.abrir_Button.clicked.connect(
            self._load_caso)

        self._main_widget.valorar_Button.clicked.connect(
            self._valorar_caso)

        self._main_widget.reset_Button.clicked.connect(
            self._reset_caso)

        self._main_window.exit_Action.triggered.connect(
            QtGui.qApp.closeAllWindows)

        self._main_window.open_file_Action.triggered.connect(
            self._load_caso)

        self._main_widget.requisitos_List.itemClicked.connect(
            self._update_requisito_fields)
        self._main_widget.requisitos_List.currentItemChanged.connect(
            self._update_requisito_fields)

        self._main_widget.valor_LineEdit.editingFinished.connect(
            self._set_valor_requisito)

        self._main_widget.valor_ComboBox.activated.connect(
            self._set_valor_requisito)

    def _load_caso(self):
        """
        Muestra la ventana de diálogo para seleccionar el archivo a abrir y lo
        abre.
        """
        # Ventana de diálogo para seleccionar el fichero.
        file_path = ValoradorMessageBoxes.open_file_dialog(
            self._view.main_window)

        self._model.opened_file_path = ""

        if(file_path):
            try:
                self._caso.load_from_JSON_file(file_path)
                self._model.opened_file_path = file_path
                self._update_entire_UI()
                ValoradorMessageBoxes.show_info_message(
                    u"Archivo cargado con éxito!")
            except Exception as e:
                self._update_entire_UI()
                ValoradorMessageBoxes.show_error_message(e.message)
                return

    def _valorar_caso(self):
        """
        Ejecuta la valoración de los requisitos del caso.
        """
        try:
            valoracion_result = self._caso.valorar()
            self._update_valoracion_fields(valoracion_result)
        except Exception as e:
            self._clean_valoracion_fields()
            ValoradorMessageBoxes.show_error_message(e.message)
            return

    def _reset_caso(self):
        """
        Reinicializa los valores de los requisitos y el resultado de la
        valoración.
        """
        confirmation = ValoradorMessageBoxes.confirm_operation_message(
            u"Perderá todos los valores introducidos en los requisitos..." +
            u"\n¿Desea continuar?")

        if (confirmation):
            self._caso.reset()
            self._update_requisito_fields()
            self._clean_valoracion_fields()

    def _set_valor_requisito(self):
        """
        Actualiza el valor del requisito seleccionado con el valor introducido.
        """
        QList = self._main_widget.requisitos_List
        selected_items = QList.selectedItems()
        selected_item_index = QList.indexFromItem(selected_items[0]).row()
        selected_requisito = self._caso.requisitos[selected_item_index]

        if(selected_requisito.tipo == "Booleano"):
            try:
                valor = self._main_widget.valor_ComboBox.currentText()
                if(valor == "True"):
                    valor = True
                elif(valor == "False"):
                    valor = False
                else:
                    valor = None
                selected_requisito.valor = valor
            except Exception as e:
                ValoradorMessageBoxes.show_error_message(e.message)
                self._update_requisito_fields()
                return
        else:
            try:
                valor = float(self._main_widget.valor_LineEdit.text())
            except Exception as e:
                ValoradorMessageBoxes.show_error_message(
                    u"Debe introducir un número!")
                self._update_requisito_fields()
                return
            try:
                selected_requisito.valor = valor
            except Exception as e:
                ValoradorMessageBoxes.show_error_message(e.message)
                self._update_requisito_fields()
                return

        self._update_requisito_fields()
        self._clean_valoracion_fields()

    def _update_entire_UI(self):
        """
        Actualiza todos los campos de la interfaz.
        """
        self._update_caso_fields()
        self._update_requisito_fields()
        self._update_requisitos_list()
        self._clean_valoracion_fields()

    def _update_caso_fields(self):
        """
        Actualiza los campos de la interfaz con la ruta y la descripión del caso.
        """
        self._main_widget.ruta_caso_LineEdit.setText(
            self._model.opened_file_path)

        self._main_widget.desc_caso_TextEdit.setText(unicode(self._caso))

    def _update_requisitos_list(self):
        """
        Carga los requisitos del caso en la lista de requisitos de la interfaz.
        """
        self._main_widget.requisitos_List.clear()

        for requisito in self._caso.requisitos:
            self._main_widget.requisitos_List.addItem(requisito.nombre)

    def _update_requisito_fields(self):
        """
        Actualiza la vista con la descripción y el valor del requisito
        seleccionado.
        """
        QList = self._main_widget.requisitos_List

        selected_items = QList.selectedItems()

        if(len(selected_items) == 1 and len(self._caso.requisitos) > 0):
            selected_item_index = QList.indexFromItem(selected_items[0]).row()

            selected_requisito = self._caso.requisitos[selected_item_index]

            self._main_widget.desc_requisito_TextEdit.setText(
                unicode(selected_requisito))

            if(selected_requisito.tipo == "Booleano"):
                self._main_widget.valor_LineEdit.setVisible(False)
                self._main_widget.valor_ComboBox.setVisible(True)

                self._main_widget.valor_ComboBox.setCurrentIndex(
                    self._main_widget.valor_ComboBox.findText(
                        str(selected_requisito.valor)
                    )
                )
            else:
                self._main_widget.valor_LineEdit.setVisible(True)
                self._main_widget.valor_ComboBox.setVisible(False)

                self._main_widget.valor_LineEdit.setText(
                    str(selected_requisito.valor)
                )
        else:
            self._main_widget.desc_requisito_TextEdit.setText("")

            self._main_widget.valor_LineEdit.setVisible(True)
            self._main_widget.valor_ComboBox.setVisible(False)

            self._main_widget.valor_LineEdit.setText("")

    def _update_valoracion_fields(self, valoracion_result):
        """
        Actualiza los campos de la interfaz con el resultado y la explicación
        de la valoración del caso.
        """
        if(valoracion_result == True):
            self._main_widget.valoracion_LineEdit.setText("APROBADO")
        else:
            self._main_widget.valoracion_LineEdit.setText("RECHAZADO")

        self._main_widget.explicacion_TextEdit.setText(self._caso.explicacion)

    def _clean_valoracion_fields(self):
        """
        Limpia los campos valoración y explicación de la vista.
        """
        self._main_widget.valoracion_LineEdit.setText("")

        self._main_widget.explicacion_TextEdit.setText("")


if __name__ == "__main__":
    """
    En caso de que intentemos ejecutar este módulo.
    """
    print(u"Este módulo no debería ser ejecutado", file=sys.stderr)
