#---------------------------------------------------------------------------
# Name:        etg/font.py
# Author:      Robin Dunn
#
# Created:     27-Nov-2010
# Copyright:   (c) 2011 by Total Control Software
# License:     wxWindows License
#---------------------------------------------------------------------------

import etgtools
import etgtools.tweaker_tools as tools

PACKAGE   = "wx"   
MODULE    = "_core"
NAME      = "font"   # Base name of the file to generate to for this script
DOCSTRING = ""

# The classes and/or the basename of the Doxygen XML files to be processed by
# this script. 
ITEMS  = [  'wxFont',
            'wxFontList',
           ]    
    
#---------------------------------------------------------------------------

def run():
    # Parse the XML file(s) building a collection of Extractor objects
    module = etgtools.ModuleDef(PACKAGE, MODULE, NAME, DOCSTRING)
    etgtools.parseDoxyXML(module, ITEMS)
    
    #-----------------------------------------------------------------
    # Tweak the parsed meta objects in the module object as needed for
    # customizing the generated code and docstrings.    
    
    c = module.find('wxFont')
    assert isinstance(c, etgtools.ClassDef)
    tools.removeVirtuals(c)
    
    c.addCppCtor("""(int pointSize,
                     wxFontFamily family,
                     int flags = wxFONTFLAG_DEFAULT,
                     const wxString& faceName = wxEmptyString,
                     wxFontEncoding encoding = wxFONTENCODING_DEFAULT)""",
        body="""\
        wxFont* font = wxFont::New(pointSize, family, flags, *faceName, encoding);
        return font;
        """)

    # Same as the above, but as a factory function
    module.addCppFunction('wxFont*', 'FFont', 
                          """(int pointSize,
                          wxFontFamily family,
                          int flags = wxFONTFLAG_DEFAULT,
                          const wxString& faceName = wxEmptyString,
                          wxFontEncoding encoding = wxFONTENCODING_DEFAULT)""",
        pyArgsString="(pointSize, family, flags=FONTFLAG_DEFAULT, faceName=EmptyString, encoding=FONTENCODING_DEFAULT)",
        body="""\
        wxFont* font = wxFont::New(pointSize, family, flags, *faceName, encoding);
        return font;
        """, factory=True)

    
    for item in c.findAll('New'):
        item.factory = True
    
    c.addProperty('Encoding GetEncoding SetEncoding')
    c.addProperty('FaceName GetFaceName SetFaceName')
    c.addProperty('Family GetFamily SetFamily')
    c.addProperty('NativeFontInfoDesc GetNativeFontInfoDesc SetNativeFontInfo')
    c.addProperty('NativeFontInfoUserDesc GetNativeFontInfoUserDesc SetNativeFontInfoUserDesc')
    c.addProperty('PointSize GetPointSize SetPointSize')
    c.addProperty('PixelSize GetPixelSize SetPixelSize')
    c.addProperty('Style GetStyle SetStyle')
    c.addProperty('Weight GetWeight SetWeight')

    # TODO, there is now a Underlined method so we can't have a
    # property of the same name.
    #c.addProperty('Underlined GetUnderlined SetUnderlined')

    c.addCppMethod('int', '__nonzero__', '()', """\
        return self->IsOk();
        """)

    
       
    # The stock Font items are documented as simple pointers, but in reality
    # they are macros that evaluate to a function call that returns a font
    # pointer, and that is only valid *after* the wx.App object has been
    # created. That messes up the code that SIP generates for them, so we need
    # to come up with another solution. So instead we will just create
    # uninitialized fonts in a block of Python code, that will then be
    # intialized later when the wx.App is created.
    c.addCppMethod('void', '_copyFrom', '(const wxFont* other)', 
                   "*self = *other;",
                   briefDoc="For internal use only.")  # ??
    pycode = '# These stock fonts will be initialized when the wx.App object is created.\n'
    for item in module:
        if '_FONT' in item.name:
            item.ignore()
            pycode += '%s = Font()\n' % tools.removeWxPrefix(item.name)
    module.addPyCode(pycode)

    # it is delay-initialized, see stockgdi.sip
    module.find('wxTheFontList').ignore()

    module.find('wxFromString').ignore()
    module.find('wxToString').ignore()


    # Some aliases that should be phased out eventually, (sooner rather than
    # later.) They are already gone (or wrapped by an #if) in the C++ code,
    # and so are not found in the documentation...
    module.addPyCode("""\
        wx.DEFAULT    = wx.FONTFAMILY_DEFAULT
        wx.DECORATIVE = wx.FONTFAMILY_DECORATIVE
        wx.ROMAN      = wx.FONTFAMILY_ROMAN
        wx.SCRIPT     = wx.FONTFAMILY_SCRIPT
        wx.SWISS      = wx.FONTFAMILY_SWISS
        wx.MODERN     = wx.FONTFAMILY_MODERN
        wx.TELETYPE   = wx.FONTFAMILY_TELETYPE

        wx.NORMAL = wx.FONTWEIGHT_NORMAL
        wx.LIGHT  = wx.FONTWEIGHT_LIGHT
        wx.BOLD   = wx.FONTWEIGHT_BOLD
        
        wx.NORMAL = wx.FONTSTYLE_NORMAL
        wx.ITALIC = wx.FONTSTYLE_ITALIC
        wx.SLANT  = wx.FONTSTYLE_SLANT
        """)        

    #-----------------------------------------------------------------
    tools.doCommonTweaks(module)
    tools.runGenerators(module)
    
    
    
#---------------------------------------------------------------------------
if __name__ == '__main__':
    run()

