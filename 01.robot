*** Settings ***
Documentation    Suite description
Library          pywinauto_core

#Test Setup      Test Start
#Test Teardown   Test Stop

*** Test Cases ***

Test Go
    # synthetic test
    # gui.py
    ${app}=         App Launch      ipyw.exe C:\\Users\\llyvin\\git_reps\\R2-D2\\ironbot\\tests\\gui_progs\\wpf\\gui.py      backend=uia

    ON ENTER TEST   ${app}

    ${win}=         GET PARENT ELEMENT          ${app}      IronPythonWPF

    ELEMENT WAIT    ${win}       ready          ${9}

    ${btn}=         GET PARENT ELEMENT          ${win}      title=Button1     auto_id=AID_Button1     control_type=Button

    DO ACTION       ${btn}                      click

    sleep           1s

    click button    ${win}                      params      title=Button1     auto_id=AID_Button1     control_type=Button

    sleep           1s

    ON LEAVE TEST