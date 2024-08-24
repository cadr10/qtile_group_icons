This is my GroupTaskList widget for qtile.

IMPORT DISCLAIMER: NOT A PROGRAMMER

![image](https://github.com/user-attachments/assets/0fba24fc-2cdb-412f-a18f-879a4114b54a)


How to use it:

Unfortenetely, I don't know how to use for multiple groups at once. For now, you need to use it for one group at time:

...

            GroupTaskList(group_name='1'),
            widget.Spacer(length=2),
            GroupTaskList(group_name='2'),
            widget.Spacer(length=2),
            GroupTaskList(group_name='3'),
            widget.Spacer(length=2),
            GroupTaskList(group_name='4'),
            widget.Spacer(length=2),
            GroupTaskList(group_name='5'),
 ...


TODO:

 - Put the spacer inside the GroupTaskList
 - One widget for multiple groups
 - Mouse actions
