*** Variables ***

${app}
${main_window}

*** Settings ***

Documentation    Suite description
Library          pywinauto_core

Test Setup      TestStart
Test Teardown   TestStop

*** Keywords ***

TestStart
    ${app}=                 App Launch      ipyw.exe C:\\Users\\llyvin\\git_reps\\R2-D2\\ironbot\\tests\\gui_progs\\wpf\\gui.py      backend=uia
    Set Global Variable     ${app}
    ON ENTER TEST           ${app}
    ${main_window}=         Get Window           ${app}         IronPythonWPF
    Set Global Variable     ${main_window}
    ELEMENT WAIT            ${main_window}       ready

TestStop
    DO ACTION               ${main_window}       close
    sleep                   1s
    ON LEAVE TEST

*** Test Cases ***

Test1
    # gui.py
    PRINT CONTROL IDENTIFIERS                   ${main_window}

    ${btn}=             GET PARENT ELEMENT      ${main_window}      title=Button1     auto_id=AID_Button1     control_type=Button
    DO ACTION           ${btn}                  click
    ${win2}=            Get Window              ${app}              AboutWindow

    DO ACTION           ${win2}                 close
    ${tbox}=            GET PARENT ELEMENT      ${main_window}      auto_id=AID_TextBox1   control_type=Edit
    CLEAR INPUT ELEMENT                         ${tbox}
    INPUT TEXT                                  ${tbox}             Hello!

Test2
    ${list_el}=         GET PARENT ELEMENT      ${main_window}      title=ABC         control_type=ListItem
    DO ACTION           ${list_el}              select
    sleep               1s
    ${list_el}=         GET PARENT ELEMENT      ${main_window}      title=DEF         control_type=ListItem
    DO ACTION           ${list_el}              select
    sleep               1s
    ${list_el}=         GET PARENT ELEMENT      ${main_window}      title=GHI         control_type=ListItem
    DO ACTION           ${list_el}              select
    sleep               1s

Test3
    ${chbx4}=           GET PARENT ELEMENT      ${main_window}      title=CheckBox1   auto_id=checkBox1   control_type=CheckBox
    SET STATE CHECKBOX  ${chbx4}                YES
    ${chbx5}=           GET PARENT ELEMENT      ${main_window}      title=CheckBox2   auto_id=checkBox2   control_type=CheckBox
    SET STATE CHECKBOX  ${chbx5}                YES
    sleep               1s

    SET STATE CHECKBOX  ${chbx4}                NO
    SET STATE CHECKBOX  ${chbx5}                NO

Test4
    ${tab1}=            GET PARENT ELEMENT      ${main_window}      title=tabItem1   auto_id=tabItem1   control_type=TabItem
    ${tab2}=            GET PARENT ELEMENT      ${main_window}      title=tabItem2   auto_id=tabItem2   control_type=TabItem
    ACTIVATE TAB        ${tab2}

    ${rb1}=             GET PARENT ELEMENT      ${main_window}      title=RadioButton1  auto_id=radioButton1  control_type=RadioButton
    ${rb2}=             GET PARENT ELEMENT      ${main_window}      title=RadioButton2  auto_id=radioButton2  control_type=RadioButton

    CLICK RADIO BUTTON  ${rb1}
    sleep               1s
    CLICK RADIO BUTTON  ${rb2}
    sleep               1s

    ACTIVATE TAB        ${tab1}

Test5
    ${ti1}=             GET PARENT ELEMENT      ${main_window}      title=Level 1       control_type=TreeItem
    ${ti2}=             GET PARENT ELEMENT      ${main_window}      title=Level 2.2     control_type=TreeItem

    TREE ITEM ACTION    ${ti2}                  collapse
    sleep               1s
    TREE ITEM ACTION    ${ti1}                  collapse
    sleep               1s

    TREE ITEM ACTION    ${ti1}                  expand
    sleep               1s
    TREE ITEM ACTION    ${ti2}                  expand
    sleep               1s