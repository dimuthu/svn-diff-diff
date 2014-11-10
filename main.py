import wx
import os
import pysvn
import shutil
import sys


class MainApp(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(500, 500))
        self.SetBackgroundColour('WHITE')
        self.init_ui()
        self.Show(True)

    def init_ui(self):
        grid = wx.FlexGridSizer(rows=9, cols=3, vgap=10, hgap=5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        empty_cell = (0, 0)

        self.lblSvnPath = wx.StaticText(self, label="SVN Path:")
        grid.Add(self.lblSvnPath)

        self.txtSvnPath = wx.TextCtrl(self, size=(300, 20))
        grid.Add(self.txtSvnPath, 1)

        self.btnBrowse = wx.Button(self, id=1, label="Browse...")
        grid.Add(self.btnBrowse, 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.btn_browse_click, self.btnBrowse)

        self.lblStartRev = wx.StaticText(self, label="Start Rev:")
        grid.Add(self.lblStartRev)

        self.txtStartRev = wx.TextCtrl(self, size=(100, 20))
        grid.Add(self.txtStartRev, 1)
        grid.Add(empty_cell)

        self.lblEndRev = wx.StaticText(self, label="End Rev:")
        grid.Add(self.lblEndRev)

        self.txtEndRev = wx.TextCtrl(self, size=(100, 20))
        grid.Add(self.txtEndRev, 1)
        grid.Add(empty_cell)

        self.lblExclude = wx.StaticText(self, label="Exclude:")
        grid.Add(self.lblExclude)

        self.txtExclude = wx.TextCtrl(self, size=(300, 20), value="*.cs")
        grid.Add(self.txtExclude, 1)

        self.btnGenDiff = wx.Button(self, id=2, label="Generate Diff")
        grid.Add(self.btnGenDiff, 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.btn_generate_diff_click, self.btnGenDiff)

        grid.Add(empty_cell)
        self.chkListFiles = wx.CheckListBox(self, size=(300, 220), style=wx.LB_HSCROLL)
        grid.Add(self.chkListFiles, 1, wx.EXPAND)
        grid.Add(empty_cell)

        self.lblExportPath = wx.StaticText(self, label="Export Path:")
        grid.Add(self.lblExportPath)

        self.txtExportPath = wx.TextCtrl(self, size=(300, 20))
        grid.Add(self.txtExportPath, 1)

        self.btnExportPathBrowse = wx.Button(self, id=3, label="Browse...")
        grid.Add(self.btnExportPathBrowse, 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.btn_browse_export_click, self.btnExportPathBrowse)

        grid.Add(empty_cell)
        self.btnExport = wx.Button(self, id=4, label="Export Files")
        grid.Add(self.btnExport, 1, wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.btn_export_click, self.btnExport)

        hbox.Add(grid, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
        self.SetSizer(hbox)

    def btn_browse_click(self, evt):
        dlg = wx.DirDialog(self, message="Choose your svn working directory")
        if dlg.ShowModal() == wx.ID_OK:
            svn_path = dlg.GetPath()
            self.txtSvnPath.SetValue(svn_path)

    def btn_browse_export_click(self, evt):
        dlg = wx.DirDialog(self, message="Choose a folder to export files")
        if dlg.ShowModal() == wx.ID_OK:
            export_path = dlg.GetPath()
            self.txtExportPath.SetValue(export_path)

    def btn_generate_diff_click(self, evt):
        try:
            self.chkListFiles.Clear()
            working_dir = self.txtSvnPath.GetValue()
            start_rev = self.txtStartRev.GetValue()
            end_rev = self.txtEndRev.GetValue()
            exclude_field = self.txtExclude.GetValue()
            exclude_list = exclude_field.split(",")
            exclude_list = self.create_extension_list(exclude_list)

            client = pysvn.Client()
            client.callback_ssl_server_trust_prompt = self.ssl_server_trust_prompt
            rev1 = pysvn.Revision(pysvn.opt_revision_kind.number, start_rev)
            rev2 = pysvn.Revision(pysvn.opt_revision_kind.number, end_rev)
            diff_files = client.diff_summarize(working_dir, rev1, working_dir, rev2, recurse=True)
            for file_obj in diff_files:
                file_extension = self.extract_extension(file_obj.path)
                if not(file_extension.upper() in exclude_list):
                    self.chkListFiles.Append(file_obj.path)
        except ValueError:
            wx.MessageBox("Invalid input", "Error", wx.OK | wx.ICON_ERROR)
        except:
            message = str(sys.exc_info()[1])
            wx.MessageBox(message, "Error", wx.OK | wx.ICON_ERROR)

    def btn_export_click(self, evt):
        file_list = self.chkListFiles.GetCheckedStrings()
        svn_path = self.txtSvnPath.GetValue()
        svn_path = svn_path.strip()
        export_path = self.txtExportPath.GetValue()
        export_path = export_path.strip()

        if export_path == "":
            wx.MessageBox("Please select a export path", "Error", wx.OK | wx.ICON_ERROR)
            return

        if not file_list:
            wx.MessageBox("files list/checked files list empty", "Error", wx.OK | wx.ICON_ERROR)
            return

        for file_name in file_list:
            if os.path.isdir(export_path):
                src = os.path.join(svn_path, file_name)
                destination = os.path.join(export_path, file_name)
                if not os.path.exists(os.path.dirname(destination)):
                    os.makedirs(os.path.dirname(destination))
                shutil.copyfile(src, destination)

        wx.MessageBox("Files are exported successfully.", "Congratulations", wx.OK | wx.ICON_INFORMATION)

    @staticmethod
    def create_extension_list(input_list):
        output = []
        for input_val in input_list:
            input_val = input_val.strip()
            input_val = input_val.split('.')
            if len(input_val) == 2:
                output.append(input_val[1].strip().upper())

        return output

    @staticmethod
    def extract_extension(filename):
        filename = filename.split('.')
        if len(filename) > 1:
            return filename[len(filename) - 1]

    @staticmethod
    def ssl_server_trust_prompt(trust_dict):
        return True, trust_dict['failures'], True


def main():
    app = wx.App(False)
    frame = MainApp(None, 'SVN Diff Diff')
    app.MainLoop()

if __name__ == '__main__':
    main()