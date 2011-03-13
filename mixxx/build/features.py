
import os
import util
from mixxx import Feature
import SCons.Script as SCons

class HSS1394(Feature):
    def description(self):
        return "HSS1394 MIDI device support"

    def enabled(self, build):
        if build.platform_is_windows or build.platform_is_osx:
            build.flags['hss1394'] = util.get_flags(build.env, 'hss1394', 1)
        else:
            build.flags['hss1394'] = util.get_flags(build.env, 'hss1394', 0)
        if int(build.flags['hss1394']):
            return True
        return False

    def add_options(self, build, vars):
        if build.platform_is_windows or build.platform_is_osx:
            vars.Add('hss1394', 'Set to 1 to enable HSS1394 MIDI device support.', 1)
        else:
            vars.Add('hss1394', 'Set to 1 to enable HSS1394 MIDI device support.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        if build.platform_is_linux:
            # TODO(XXX) Enable this when when FFADO back-end support is written into Mixxx
            return
            #have_ffado = conf.CheckLib('ffado', autoadd=False)
            #if not have_ffado:
            #    raise Exception('Could not find libffado.')
        else:
#            if not conf.CheckHeader('HSS1394/HSS1394.h'):  # WTF this gives tons of errors on MSVC
#                raise Exception('Did not find HSS1394 development headers, exiting!')
#            elif not conf.CheckLib(['libHSS1394', 'HSS1394']):
            if not conf.CheckLib(['libHSS1394', 'HSS1394']):
                raise Exception('Did not find HSS1394 development library, exiting!')
                return

        build.env.Append(CPPDEFINES = '__HSS1394__')

    def sources(self, build):
        sources = SCons.Split("""midi/mididevicehss1394.cpp
                            midi/hss1394enumerator.cpp
                            """)
        return sources


class Mad(Feature):
    def description(self):
        return "MAD MP3 Decoder"

    def enabled(self, build):
        build.flags['mad'] = util.get_flags(build.env, 'mad', 1)
        if int(build.flags['mad']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('mad', 'Set to 1 to enable MAD MP3 decoder support.', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        if not conf.CheckLib(['libmad','mad']):
            raise Exception('Did not find libmad.a, libmad.lib, or the libmad development header files - exiting!')
        if not conf.CheckLib(['libid3tag', 'id3tag','libid3tag-release']):
            raise Exception('Did not find libid3tag.a, libid3tag.lib, or the libid3tag development header files - exiting!')
        build.env.Append(CPPDEFINES = '__MAD__')

    def sources(self, build):
        return ['soundsourcemp3.cpp']


class CoreAudio(Feature):

    def description(self):
        return "CoreAudio MP3/AAC Decoder"

    def enabled(self, build):
        build.flags['coreaudio'] = util.get_flags(build.env, 'coreaudio', 0)
        if int(build.flags['coreaudio']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('coreaudio', 'Set to 1 to enable CoreAudio MP3/AAC decoder support.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        if not build.platform_is_osx:
            raise Exception('CoreAudio is only supported on OS X!');
        else:
            build.env.Append(CPPPATH='/System/Library/Frameworks/AudioToolbox.framework/Headers/')
            build.env.Append(CPPPATH='#lib/apple/')
            build.env.Append(LINKFLAGS='-framework AudioToolbox -framework CoreFoundation')
            build.env.Append(CPPDEFINES = '__COREAUDIO__')

    def sources(self, build):
        return ['soundsourcecoreaudio.cpp',
                '#lib/apple/CAStreamBasicDescription.h']


class MIDIScript(Feature):
    def description(self):
        return "MIDI Scripting"

    def enabled(self, build):
        build.flags['midiscript'] = util.get_flags(build.env, 'midiscript', 0)
        if int(build.flags['midiscript']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('midiscript', 'Set to 1 to enable MIDI Scripting support.', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        if build.platform_is_windows:
            build.env.Append(LIBS = 'QtScript4')
        elif build.platform_is_linux:
                build.env.Append(LIBS = 'QtScript')
        elif build.platform_is_osx:
                # TODO(XXX) put in logic here to add a -framework QtScript
                pass
        build.env.Append(CPPPATH = '$QTDIR/include/QtScript')
        build.env.Append(CPPDEFINES = '__MIDISCRIPT__')

    def sources(self, build):
        return ["midi/midiscriptengine.cpp"]

class LADSPA(Feature):

    def description(self):
        return "Experimental LADSPA Support"

    def enabled(self, build):
        enabled = util.get_flags(build.env, 'ladspa', 0)
        build.flags['ladspa'] = enabled
        return True if int(enabled) else False

    def add_options(self, build, vars):
        vars.Add('ladspa', '(EXPERIMENTAL) Set to 1 to enable LADSPA plugin support', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        build.env.Append(CPPPATH=['#lib/ladspa'])
        build.env.Append(CPPDEFINES = '__LADSPA__')

    def sources(self, build):
        ladspa_plugins = SCons.SConscript(SCons.File('#lib/ladspa/SConscript'))
        #build.env.Alias('plugins', ladspa_plugins)
        sources = SCons.Split("""engine/engineladspa.cpp
                            ladspa/ladspaloader.cpp
                            ladspa/ladspalibrary.cpp
                            ladspa/ladspaplugin.cpp
                            ladspa/ladspainstance.cpp
                            ladspa/ladspacontrol.cpp
                            ladspa/ladspainstancestereo.cpp
                            ladspa/ladspainstancemono.cpp
                            ladspaview.cpp
                            ladspa/ladspapreset.cpp
                            ladspa/ladspapresetmanager.cpp
                            ladspa/ladspapresetknob.cpp
                            ladspa/ladspapresetinstance.cpp
                            dlgladspa.cpp
                            ladspa/ladspapresetslot.cpp
                            """)
        return ladspa_plugins + sources



class IPod(Feature):
    def description(self):
        return "NOT-WORKING iPod Support"

    def enabled(self, build):
        build.flags['ipod'] = util.get_flags(build.env, 'ipod', 0)
        if int(build.flags['ipod']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('ipod', 'Set to 1 to enable iPod support through libgpod', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        build.env.Append(CPPDEFINES = '__IPOD__')
        if build.platform_is_windows:
            build.env.Append(LIBS = 'gpod');
            # You must check v-this-v directory out from http://publicsvn.songbirdnest.com/vendor-binaries/trunk/windows-i686-msvc8/libgpod/
            build.env.Append(LIBPATH='../../../windows-i686-msvc8/libgpod/release/lib')
            # Following building the following must be added to the dist folder in order for mixxx to run with ipod support on Windows
            # \windows-i686-msvc8\libgpod\release\lib\libgpod.dll
            # \windows-i686-msvc8\glib\release\bin\libgobject-2.0-0.dll
            # \windows-i686-msvc8\glib\release\bin\libglib-2.0-0.dll
            # \windows-i686-msvc8\libiconv\release\bin\iconv.dll
            # \windows-i686-msvc8\gettext\release\binintl.dll
        if build.platform_is_linux or build.platform_is_osx:
            # env.Append(LIBS = 'libgpod-1.0')
            # env.Append(LIBS = 'glib-2.0')
            build.env.ParseConfig('pkg-config libgpod-1.0 --silence-errors --cflags --libs')
            build.env.ParseConfig('pkg-config glib-2.0 --silence-errors --cflags --libs')

    def sources(self, build):
        return ['wipodtracksmodel.cpp']

class MSVCDebug(Feature):
    def description(self):
        return "MSVC Debugging"

    def enabled(self, build):
        build.flags['msvcdebug'] = util.get_flags(build.env, 'msvcdebug', 0)
        if int(build.flags['msvcdebug']):
            return True
        return False

    def add_options(self, build, vars):
        if build.toolchain_is_msvs:
            vars.Add('msvcdebug', 'Set to 1 to link against MS libraries with debugging info (implies debug=1)', 0)

    def configure(self, build, conf):
        if self.enabled(build):
            if not build.toolchain_is_msvs:
                raise Exception("Error, msvcdebug flag set when toolchain is not MSVS.")

            # Enable debug multithread and DLL specific runtime methods. Required
            # for sndfile w/ flac support on windows.
            build.env.Append(CCFLAGS = '/MDd')
            build.env.Append(LINKFLAGS = '/DEBUG')
            build.env.Append(CPPDEFINES = 'DEBUGCONSOLE')
            if build.machine_is_64bit:
                build.env.Append(CCFLAGS = '/Zi')
                build.env.Append(LINKFLAGS = '/NODEFAULTLIB:MSVCRT')
            else:
                build.env.Append(CCFLAGS = '/ZI')
        elif build.toolchain_is_msvs:
            # Enable multithreaded and DLL specific runtime methods. Required
            # for sndfile w/ flac support on windows
            build.env.Append(CCFLAGS = '/MD')


class HifiEq(Feature):
    def description(self):
        return "High quality EQs"

    def enabled(self, build):
        build.flags['hifieq'] = util.get_flags(build.env, 'hifieq', 1)
        if int(build.flags['hifieq']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('hifieq', 'Set to 1 to enable high quality EQs', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            # Enables old crappy EQs
            build.env.Append(CPPDEFINES = ['__LOFI__', '__NO_INTTYPES__'])

class VinylControl(Feature):
    def description(self):
        return "Vinyl Control"

    def enabled(self, build):
        build.flags['vinylcontrol'] = util.get_flags(build.env, 'vinylcontrol', 0)
        if int(build.flags['vinylcontrol']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('vinylcontrol', 'Set to 1 to enable vinyl control support', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        build.env.Append(CPPDEFINES = '__VINYLCONTROL__')
        build.env.Append(CPPPATH='#lib/xwax')
        build.env.Append(CPPPATH='#lib/scratchlib')

    def sources(self, build):
        sources = ['vinylcontrol.cpp',
                   'vinylcontrolproxy.cpp',
                   'vinylcontrolxwax.cpp',
                   'dlgprefvinyl.cpp',
                   'vinylcontrolsignalwidget.cpp']
        if build.platform_is_windows:
            sources.append("#lib/xwax/timecoder_win32.cpp")
        else:
            sources.append("#lib/xwax/timecoder.c")
            sources.append("#lib/xwax/lut.c")
        
        return sources

class Tonal(Feature):
    def description(self):
        return "NOT-WORKING Tonal Audio Detection"

    def enabled(self, build):
        build.flags['tonal'] = util.get_flags(build.env, 'tonal', 0)
        if int(build.flags['tonal']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('tonal', 'Set to 1 to enable tonal analysis', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

    def sources(self, build):
        sources = ['tonal/FourierTransform.cxx',
                   'tonal/Segmentation.cxx',
                   'tonal/tonalanalyser.cpp',
                   'tonal/ConstantQTransform.cxx',
                   'tonal/ConstantQFolder.cxx']
        return sources

class FAAD(Feature):
    def description(self):
        return "FAAD AAC audio file decoder plugin"

    def enabled(self, build):
        build.flags['faad'] = util.get_flags(build.env, 'faad', 0)
        if int(build.flags['faad']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('faad', 'Set to 1 to enable building the FAAD AAC decoder plugin.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        have_mp4v2_h = conf.CheckHeader('mp4v2/mp4v2.h')
        have_mp4v2 = conf.CheckLib(['mp4v2','libmp4v2'], autoadd=False)
        have_mp4 = conf.CheckLib('mp4', autoadd=False)

        # Either mp4 or mp4v2 works
        have_mp4 = (have_mp4v2_h and have_mp4v2) or have_mp4

        if not have_mp4:
            raise Exception('Could not find libmp4, libmp4v2 or the libmp4v2 development headers.')

        have_faad = conf.CheckLib(['faad','libfaad'], autoadd=False)

        if not have_faad:
            raise Exception('Could not find libfaad or the libfaad development headers.')


class WavPack(Feature):
    def description(self):
        return "WavPack audio file support plugin"

    def enabled(self, build):
        build.flags['wv'] = util.get_flags(build.env, 'wv', 0)
        if int(build.flags['wv']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('wv', 'Set to 1 to enable building the WavPack support plugin.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        have_wv = conf.CheckLib(['wavpack', 'wv'], autoadd=False)
        if not have_wv:
            raise Exception('Could not find libwavpack, libwv or its development headers.')


class ScriptStudio(Feature):
    def description(self):
        return "NOT-WORKING MixxxScript Studio"

    def enabled(self, build):
        build.flags['script'] = util.get_flags(build.env, 'script', 0)
        if int(build.flags['script']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('script', 'Set to 1 to enable MixxxScript/QtScript Studio support.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        build.env.Append(CPPDEFINES = '__SCRIPT__')

    def sources(self, build):
        build.env.Uic4('script/scriptstudio.ui')
        return ['script/scriptengine.cpp',
                'script/scriptcontrolqueue.cpp',
                'script/scriptstudio.cpp',
                'script/scriptrecorder.cpp',
                'script/playinterface.cpp',
                'script/macro.cpp',
                'script/scriptcontrolevent.cpp',
                'script/trackcontrolevent.cpp',
                'script/numbercontrolevent.cpp',
                'script/numberrecorder.cpp',
                'script/macrolist.cpp',
                'script/trackrecorder.cpp',
                'script/sdatetime.cpp',
                'script/signalrecorder.cpp',
                'script/macrolistitem.cpp',
                'script/qtscriptinterface.cpp']

class AsmLib(Feature):
    def description(self):
        return "Agner Fog\'s ASMLIB"

    def enabled(self, build):
        build.flags['asmlib'] = util.get_flags(build.env, 'asmlib', 0)
        if int(build.flags['asmlib']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('asmlib','Set to 1 to enable linking against Agner Fog\'s hand-optimized asmlib, found at http://www.agner.org/optimize/', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        build.env.Append(LIBPATH='#/../asmlib')
        if build.platform_is_linux:
            build.env.Append(CCFLAGS = '-fno-builtin')   #Use ASMLIB's functions instead of the compiler's
            build.env.Append(LIBS = '":alibelf%so.a"' % build.bitwidth)
        elif build.platform_is_osx:
            build.env.Append(CCFLAGS = '-fno-builtin')   #Use ASMLIB's functions instead of the compiler's
            build.env.Append(LIBS = '":alibmac%so.a"' % build.bitwidth)
        elif build.platform_is_windows:
            build.env.Append(CCFLAGS = '/Oi-')   #Use ASMLIB's functions instead of the compiler's
            build.env.Append(LIBS = 'alibcof%so' % build.bitwidth)


class QDebug(Feature):
    def description(self):
        return "Debugging message output"

    def enabled(self, build):
        # Meh, repeating this can't hurt, and we require knowing the status of msvcdebug.
        build.flags['msvcdebug'] = util.get_flags(build.env, 'msvcdebug', 0)
        build.flags['qdebug'] = util.get_flags(build.env, 'qdebug', 0)
        if build.platform_is_windows:
            if int(build.flags['msvcdebug']):
                # Turn general debugging flag on too if msvcdebug is specified
                build.flags['qdebug'] = 1
        if int(build.flags['qdebug']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('qdebug', 'Set to 1 to enable verbose console debug output.', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            build.env.Append(CPPDEFINES = 'QT_NO_DEBUG_OUTPUT')

class CMetrics(Feature):
    def description(self):
        return "NOT-WORKING CMetrics Reporting"

    def enabled(self, build):
        if build.platform_is_windows or build.platform_is_linux:
            build.flags['cmetrics'] = util.get_flags(build.env, 'cmetrics', 1)
        else:
            # Off on OS X for now...
            build.flags['cmetrics'] = util.get_flags(build.env, 'cmetrics', 0)
        if int(build.flags['cmetrics']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('cmetrics', 'Set to 1 to enable crash reporting/usage statistics via Case Metrics (This should be disabled on development builds)', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        build.env.Append(CPPDEFINES = '__C_METRICS__')

        if build.platform_is_windows:
            build.env.Append(LIBS = 'cmetrics')
        else:
            client = 'MIXXX'
            server = 'metrics.mixxx.org' # mixxx metrics collector
            SCons.Export('client server')
            build.env.Append(CPPPATH='#lib/cmetrics')

    def sources(self, build):
        return ['#lib/cmetrics/SConscript']

class MSVSHacks(Feature):
    """Visual Studio 2005 hacks (MSVS Express Edition users shouldn't enable
    this)"""

    def description(self):
        return "MSVS 2005 hacks"

    def enabled(self, build):
        build.flags['msvshacks'] = util.get_flags(build.env, 'msvshacks', 0)
        if int(build.flags['msvshacks']):
            return True
        return False

    def add_options(self, build, vars):
        if build.toolchain_is_msvs:
            vars.Add('msvshacks', 'Set to 1 to build properly with MS Visual Studio 2005 (Express users should leave this off)', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        build.env.Append(CPPDEFINES = '__MSVS2005__')

class Profiling(Feature):
    def description(self):
        return "gprof/Saturn profiling support"

    def enabled(self, build):
        build.flags['profiling'] = util.get_flags(build.env, 'profiling', 0)
        if int(build.flags['profiling']):
            if build.platform_is_linux or build.platform_is_osx or build.platform_is_bsd:
                return True
        return False

    def add_options(self, build, vars):
        if not build.platform_is_windows:
            vars.Add('profiling', '(DEVELOPER) Set to 1 to enable profiling using gprof (Linux) or Saturn (OS X)', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return
        if build.platform_is_linux or build.platform_is_bsd:
            build.env.Append(CCFLAGS = '-pg')
            build.env.Append(LINKFLAGS = '-pg')
        elif build.platform_is_osx:
            build.env.Append(CCFLAGS = '-finstrument-functions')
            build.env.Append(LINKFLAGS = '-lSaturn')

class TestSuite(Feature):
    def description(self):
        return "Mixxx Test Suite"

    def enabled(self, build):
        build.flags['test'] = util.get_flags(build.env, 'test', 0) or \
            'test' in SCons.BUILD_TARGETS
        if int(build.flags['test']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('test', 'Set to 1 to build Mixxx test fixtures.', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

    def sources(self, build):
        # Build the gtest library, but don't return any sources.

        # Clone our main environment so we don't change any settings in the
        # Mixxx environment
        test_env = build.env.Clone()

        # -pthread tells GCC to do the right thing regardless of system
        test_env.Append(CCFLAGS = '-pthread')
        test_env.Append(LINKFLAGS = '-pthread')

        test_env.Append(CPPPATH="#lib/gtest-1.5.0/include")
        gtest_dir = test_env.Dir("#lib/gtest-1.5.0")
        #gtest_dir.addRepository(build.env.Dir('#lib/gtest-1.5.0'))
        #build.env['EXE_OUTPUT'] = '#/lib/gtest-1.3.0/bin'  # example, optional
        test_env['LIB_OUTPUT'] = '#/lib/gtest-1.5.0/lib'

        env = test_env
        SCons.Export('env')
        env.SConscript(env.File('SConscript', gtest_dir))

        # build and configure gmock
        test_env.Append(CPPPATH="#lib/gmock-1.5.0/include")
        gmock_dir = test_env.Dir("#lib/gmock-1.5.0")
        #gmock_dir.addRepository(build.env.Dir('#lib/gmock-1.5.0'))
        test_env['LIB_OUTPUT'] = '#/lib/gmock-1.5.0/lib'

        env.SConscript(env.File('SConscript', gmock_dir))

        return []

class Shoutcast(Feature):
    def description(self):
        return "Shoutcast Broadcasting (OGG/MP3)"

    def enabled(self, build):
        build.flags['shoutcast'] = util.get_flags(build.env, 'shoutcast', 1)
        if int(build.flags['shoutcast']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('shoutcast', 'Set to 1 to enable shoutcast support', 1)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        libshout_found = conf.CheckLib(['libshout','shout'])
        build.env.Append(CPPDEFINES = '__SHOUTCAST__')

        if not libshout_found:
            raise Exception('Could not find libshout or its development headers. Please install it or compile Mixxx without Shoutcast support using the shoutcast=0 flag.')

        # libvorbisenc does only exist on Linux and OSX, on Windows it is
        # included in vorbisfile.dll
        if not build.platform_is_windows:
            vorbisenc_found = conf.CheckLib(['vorbisenc'])
            if not vorbisenc_found:
                raise Exception("libvorbisenc was not found! Please install it or compile Mixxx without Shoutcast support using the shoutcast=0 flag.")

    def sources(self, build):
        build.env.Uic4('dlgprefshoutcastdlg.ui')
        return ['dlgprefshoutcast.cpp',
                'engine/engineshoutcast.cpp',
                'recording/encodervorbis.cpp',
                'recording/encodermp3.cpp']


class FFMPEG(Feature):
    def description(self):
        return "NOT-WORKING FFMPEG support"

    def enabled(self, build):
        build.flags['ffmpeg'] = util.get_flags(build.env, 'ffmpeg', 0)
        if int(build.flags['ffmpeg']):
            return True
        return False

    def add_options(self, build, vars):
        vars.Add('ffmpeg', '(NOT-WORKING) Set to 1 to enable FFMPEG support', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            return

        if build.platform_is_linux or build.platform_is_osx or build.platform_is_bsd:
            # Check for libavcodec, libavformat
            # I just randomly picked version numbers lower than mine for this - Albert
            if not conf.CheckForPKG('libavcodec', '51.20.0'):
                raise Exception('libavcodec not found.')
            if not conf.CheckForPKG('libavformat', '51.1.0'):
                raise Exception('libavcodec not found.')
            #Grabs the libs and cflags for ffmpeg
            build.env.ParseConfig('pkg-config libavcodec --silence-errors --cflags --libs')
            build.env.ParseConfig('pkg-config libavformat --silence-errors --cflags --libs')
            build.env.Append(CPPDEFINES = '__FFMPEGFILE__')
        else:
            # aptitude install libavcodec-dev libavformat-dev liba52-0.7.4-dev libdts-dev
            build.env.Append(LIBS = 'avcodec')
            build.env.Append(LIBS = 'avformat')
            build.env.Append(LIBS = 'z')
            build.env.Append(LIBS = 'a52')
            build.env.Append(LIBS = 'dts')
            build.env.Append(LIBS = 'gsm')
            build.env.Append(LIBS = 'dc1394_control')
            build.env.Append(LIBS = 'dl')
            build.env.Append(LIBS = 'vorbisenc')
            build.env.Append(LIBS = 'raw1394')
            build.env.Append(LIBS = 'avutil')
            build.env.Append(LIBS = 'vorbis')
            build.env.Append(LIBS = 'm')
            build.env.Append(LIBS = 'ogg')
            build.env.Append(CPPDEFINES = '__FFMPEGFILE__')

    def sources(self, build):
        return ['soundsourceffmpeg.cpp']

class Optimize(Feature):
    def description(self):
        return "Optimization and Tuning"

    def enabled(self, build):
        # Meh, repeating this can't hurt, and we require knowing the status of msvcdebug.
        build.flags['msvcdebug'] = util.get_flags(build.env, 'msvcdebug', 0)
        build.flags['optimize'] = util.get_flags(build.env, 'optimize', 1)
        if int(build.flags['optimize']):
            return True
        else:
            return False

    def add_options(self, build, vars):
        if not build.platform_is_windows:
            vars.Add('optimize', 'Set to:\n  1 for -O3 compiler optimizations\n  2 for Pentium 4 optimizations\n  3 for Intel Core optimizations\n  4 for Intel Core 2 optimizations\n  5 for Athlon-4/XP/MP optimizations\n  6 for K8/Opteron/AMD64 optimizations\n  7 for K8/Opteron/AMD64 w/ SSE3\n  8 for Celeron D (generic SSE/SSE2/SSE3) optimizations.', 1)
        else:
            if build.machine_is_64bit:
                vars.Add('optimize', 'Set to:\n  1 to maximize speed (/O2)\n  2 for maximum optimizations (/Ox)', 1)
            else:
                vars.Add('optimize', 'Set to:\n  1 to maximize speed (/O2)\n  2 for maximum optimizations (/Ox)\n  3 to use SSE instructions\n  4 to use SSE2 instructions', 1)


    def configure(self, build, conf):
        if not self.enabled(build):
            return

        optimize_level = int(build.flags['optimize'])

        if build.toolchain_is_msvs:
            if int(build.flags['msvcdebug']):
                self.status = "Disabled (due to mscvdebug mode)"
                return
            # Valid values of /MACHINE are:
            # {AM33|ARM|EBC|IA64|M32R|MIPS|MIPS16|MIPSFPU|MIPSFPU16|MIPSR41XX|SH3|SH3DSP|SH4|SH5|THUMB|X86}
            # http://msdn.microsoft.com/en-us/library/5wy54dk2(v=VS.71).aspx
            if build.machine_is_64bit:
                build.env.Append(LINKFLAGS = '/MACHINE:X64')
            else:
                build.env.Append(LINKFLAGS = '/MACHINE:'+build.machine)

            # /GL : http://msdn.microsoft.com/en-us/library/0zza0de8.aspx
            # /MP : http://msdn.microsoft.com/en-us/library/bb385193.aspx
            # /MP has little to do with optimization so why is it here?
            # !!! /GL is incompatible with /ZI, which is set by mscvdebug
            build.env.Append(CCFLAGS = '/GL /MP')

            # Use the fastest floating point math library
            # http://msdn.microsoft.com/en-us/library/e7s85ffb.aspx
            # http://msdn.microsoft.com/en-us/library/ms235601.aspx
            build.env.Append(CCFLAGS = '/fp:fast')

            # Do link-time code generation (and show a progress indicator)
            # Should we turn on PGO ?
            # http://msdn.microsoft.com/en-us/library/xbf3tbeh.aspx
            build.env.Append(LINKFLAGS = '/LTCG:STATUS')

            # Suggested for unused code removal
            # http://msdn.microsoft.com/en-us/library/ms235601.aspx
            # http://msdn.microsoft.com/en-us/library/xsa71f43.aspx
            # http://msdn.microsoft.com/en-us/library/bxwfs976.aspx
            build.env.Append(CCFLAGS = '/Gy')
            build.env.Append(LINKFLAGS = '/OPT:REF')
            build.env.Append(LINKFLAGS = '/OPT:ICF')

            # http://msdn.microsoft.com/en-us/library/59a3b321.aspx
            # In general, you should pick /O2 over /Ox
            if optimize_level >= 1:
                self.status = "Enabled -- Maximize Speed (/O2)"
                build.env.Append(CCFLAGS = '/O2')
            #elif optimize_level >= 2:
            #    self.status = "Enabled -- Maximum Optimizations (/Ox)"
            #    build.env.Append(CCFLAGS = '/Ox')

            # SSE and SSE2 are core instructions on x64
            if not build.machine_is_64bit:
                if optimize_level == 3:
                    self.status += ", SSE Instructions Enabled"
                    build.env.Append(CCFLAGS = '/arch:SSE')
                elif optimize_level == 4:
                    self.status += ", SSE2 Instructions Enabled"
                    build.env.Append(CCFLAGS = '/arch:SSE2')
        elif build.toolchain_is_gnu:
            if int(build.flags.get('tuned',0)):
                self.status = "Disabled (Overriden by tuned=1)"
                return

            # Common flags to all optimizations. Consider dropping -O3 to -O2
            # and getting rid of -fomit-frame-pointer, -ffast-math, and
            # -funroll-loops. We need to justify our use of these aggressive
            # optimizations with data.
            build.env.Append(CCFLAGS='-O3 -fomit-frame-pointer -ffast-math -funroll-loops')

            if optimize_level == 1:
                # only includes what we already applied
                self.status = "Enabled -- Basic Optimizations (-03)"
            elif optimize_level == 2:
                self.status = "Enabled (P4 MMX/SSE)"
                build.env.Append(CCFLAGS = '-march=pentium4 -mmmx -msse2 -mfpmath=sse')
            elif optimize_level == 3:
                self.status = "Enabled (Intel Core Solo/Duo)"
                build.env.Append(CCFLAGS = '-march=prescott -mmmx -msse3 -mfpmath=sse')
            elif optimize_level == 4:
                self.status = "Enabled (Intel Core 2)"
                build.env.Append(CCFLAGS = '-march=nocona -mmmx -msse -msse2 -msse3 -mfpmath=sse -ffast-math -funroll-loops')
            elif optimize_level == 5:
                self.status = "Enabled (Athlon Athlon-4/XP/MP)"
                build.env.Append(CCFLAGS = '-march=athlon-4 -mmmx -msse -m3dnow -mfpmath=sse')
            elif optimize_level == 6:
                self.status = "Enabled (Athlon K8/Opteron/AMD64)"
                build.env.Append(CCFLAGS = '-march=k8 -mmmx -msse2 -m3dnow -mfpmath=sse')
            elif optimize_level == 7:
                self.status = "Enabled (Athlon K8/Opteron/AMD64 + SSE3)"
                build.env.Append(CCFLAGS = '-march=k8-sse3 -mmmx -msse2 -msse3 -m3dnow -mfpmath=sse')
            elif optimize_level == 8:
                self.status = "Enabled (Generic SSE/SSE2/SSE3)"
                build.env.Append(CCFLAGS = '-mmmx -msse2 -msse3 -mfpmath=sse')
            elif optimize_level == 9:
                self.status = "Enabled (Tuned Generic)"
                # This option is for release builds packaged for 64-bit. We
                # don't know what kind of 64-bit CPU they'll have, so let
                # -mtune=generic pick the best options. Used by the debian rules
                # script.

                # It's a little sketchy, but I'm turning on SSE and MMX by
                # default. opt=9 is a distribution mode, we don't really support
                # CPU's earlier than Pentium 3, which is the class of CPUs this
                # decision affects. The downside of this is that we aren't truly
                # i386 compatible, so builds that claim 'i386' will crash.
                # -- rryan 2/2011

                # TODO(XXX) check the soundtouch package in Ubuntu to see what they do about this.
                build.env.Append(CCFLAGS = '-mtune=generic -mmmx -msse -mfpmath=sse')

                # Enable SSE2 on 64-bit machines. SSE3 is not a sure thing on 64-bit
                if build.machine_is_64bit:
                    build.env.Append(CCFLAGS = '-msse2')


class Tuned(Feature):
    def description(self):
        return "Optimizing for this CPU"

    def enabled(self, build):
        build.flags['tuned'] = util.get_flags(build.env, 'tuned', 0)
        if int(build.flags['tuned']):
            return True
        return False

    def add_options(self, build, vars):
        if not build.platform_is_windows:
            vars.Add('tuned', 'Set to 1 to optimize mixxx for this CPU (overrides "optimize")', 0)
        elif build.machine_is_64bit: # 64-bit windows
            vars.Add('tuned', 'Set to 1 to optimize mixxx for this CPU class', 0)

    def configure(self, build, conf):
        if not self.enabled(build):
            # Even if not enabled, enable 'blending' for 64-bit because the
            # instructions are emitted anyway.
            if build.toolchain_is_msvs and build.machine_is_64bit:
                build.env.Append(CCFLAGS = '/favor:blend')
            return

        if build.toolchain_is_gnu:
            ccv = build.env['CCVERSION'].split('.')
            if int(ccv[0]) >= 4 and int(ccv[1]) >= 2:
                # Should we use -mtune as well?
                build.env.Append(CCFLAGS = '-march=native')
                # Doesn't make sense as a linkflag
                build.env.Append(LINKFLAGS = '-march=native')
            else:
                self.status = "Disabled (requires gcc >= 4.2.0)"
        elif build.toolchain_is_msvs:
            if build.machine_is_64bit:
                if 'makerelease' in SCons.COMMAND_LINE_TARGETS:
                    self.status = "Disabled (due to makerelease target)"
                    # AMD64 is for AMD CPUs, EM64T is for Intel x64 ones (as opposed to
                    # IA64 which uses a different compiler.)  For a release, we choose
                    # to have code run about the same on both
                    build.env.Append(CCFLAGS = '/favor:blend')
                else:
                    #self.status = "Disabled (currently broken with Visual Studio)"
                    #build.env.Append(CCFLAGS = '/favor:blend')
                    # Only valid choices are AMD64, EM64T (INTEL64 on later compilers,)
                    # and blend.
                    self.status = "Enabled (%s-optimized)" % build.machine
                    build.env.Append(CCFLAGS = '/favor:' + build.machine)
            else:
                self.status = "Disabled (not supported on 32-bit MSVC)"
