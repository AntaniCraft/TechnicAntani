from unittest import TestCase
from django.test import TestCase as DTest
from TechnicAntani.antanisettings import MODPACKPATH
from api.models import ModCache, ModpackCache, VersionCache, ModInfoCache,ApiKey
import mock
from django.test import RequestFactory
import json
from urllib.parse import urlparse

class ModelTest(TestCase):

    def test_modcache_get_filename(self):
        m = ModCache()
        m.localpath = "/home/lulz/awesome.png"
        self.assertEqual(m.get_filename(),"awesome.png")

    def test_modcache_geturl(self):

        req_fact = RequestFactory()
        req = req_fact.get('/')
        m= ModCache()
        m.localpath = '/home/test/awesome.png'
        parsed = urlparse(m.get_url(req))
        self.assertEqual(parsed.scheme, 'http')
        self.assertTrue(parsed.path.find('awesome.png') != -1)


class ViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        cls.first=ModpackCache(name='test_d',slug='test',url='http://nope.org',description='test',logo_md5='',icon_md5='', background_md5='')
        cls.first.save()
        tmp=VersionCache(version='1.0', recommended=True, latest=False,modpack=cls.first, mcversion='1.6.4',forgever='nover')
        tmp.save()
        VersionCache(version='1.1dev', recommended=False, latest=True,modpack=cls.first, mcversion='1.6.4',forgever='').save()
        t = ModInfoCache(name='mod',pretty_name='pretty_mod',author='me',description='mod_d',link='http://nope.org')
        t.save()
        m = ModCache(localpath='/etc/issue',version='1.0',modInfo=t,md5='somemd5')
        m.save()
        m = ModCache(localpath='/etc/issue2',version='1.2',modInfo=t,md5='somemd52')
        m.save()
        tmp.mods.add(m)
        t = ModInfoCache(name='mod2',pretty_name='pretty_mod2',author='me2',description='mod_d2',link='http://nope2.org')
        t.save()
        m = ModCache(localpath='/etc/issue3',version='1.03',modInfo=t,md5='somemd53')
        m.save()
        ModpackCache(name='test2',slug='test2',url='http://nope.org',description='test2',logo_md5='',icon_md5='', background_md5='').save()
        tmp.mods.add(m)
        ApiKey(key='somekey',description='mykey').save()
        ApiKey(key='somekey2',description='mykey').save()

    def test_api_resolve(self):
        from django.core.urlresolvers import resolve
        from .views import index, modpack_list, modpack, modpack_build, verify, mod
        self.assertEqual(resolve('/api/').func, index)
        self.assertEqual(resolve('/api/modpack/').func, modpack_list)
        self.assertEqual(resolve('/api/modpack').func, modpack_list)
        self.assertEqual(resolve('/api/modpack/test').func, modpack)
        self.assertEqual(resolve('/api/modpack/test/').func, modpack)
        self.assertEqual(resolve('/api/modpack/test/version').func, modpack_build)
        self.assertEqual(resolve('/api/modpack/test/version/').func, modpack_build)
        self.assertEqual(resolve('/api/verify/').func, verify)
        self.assertEqual(resolve('/api/verify/test').func, verify)
        self.assertEqual(resolve('/api/verify/test/').func, verify)
        self.assertEqual(resolve('/api/mod/').func, mod)
        self.assertEqual(resolve('/api/mod/test').func, mod)
        self.assertEqual(resolve('/api/mod/test/').func, mod)

    def test_apiversion(self):
        from .views import index
        r = self.factory.get('/api/')
        out = index(r)
        obj = json.loads(out.content.decode())
        self.assertEqual(obj['api'],'TechnicSolder')
        self.assertEqual(obj['version'], '0.3')
        self.assertEqual(obj['extraver'], '0.1antani')
        self.assertEqual(obj['stream'], 'DEV')

    def test_modpack_list(self):
        from .views import modpack_list
        r = self.factory.get('/api/modpack/')
        out = modpack_list(r)
        obj = json.loads(out.content.decode())
        self.assertTrue(len(obj['modpacks']) == 2)
        self.assertTrue(urlparse(obj['mirror_url']).scheme.startswith('http'))

    def test_modpack(self):
        from .views import modpack
        r = self.factory.get('/api/modpack/test/')
        out = modpack(r, 'test')
        obj = json.loads(out.content.decode())
        expected = {
            'name': 'test',
            'display_name': 'test_d',
            'url': 'http://nope.org',
            'logo_md5' : '',
            'icon_md5':'',
            'background_md5':'',
            'builds': ['1.0','1.1dev'],
            'latest': '1.1dev',
            'recommended': '1.0'
        }
        self.assertDictEqual(obj,expected)

    def test_modpack_version(self):
        from .views import modpack_build
        r = self.factory.get('/api/modpack/test/1.0')
        out = json.loads(modpack_build(r,'test','1.0').content.decode())
        expected = {
            'forge': 'nover',
            'minecraft': '1.6.4',
            'minecraft_md5': '',
            'mods': [
                {
                    'version': '1.2',
                    'name': 'mod',
                    'md5': 'somemd52',
                    'url': 'http://testserver/antani/mods/issue2'
                },
                {
                    'version': '1.03',
                    'name': 'mod2',
                    'md5': 'somemd53',
                    'url': 'http://testserver/antani/mods/issue3'
                }
            ]}
        self.assertDictEqual(out,expected)

    def test_verify(self):
        from .views import verify
        r = self.factory.get('/api/verify/somekey')
        out = json.loads(verify(r,'somekey').content.decode())
        expected = {
            'valid': 'Key validated.'
        }
        self.assertDictEqual(out,expected)
        r = self.factory.get('/api/verify/somekey2')
        out = json.loads(verify(r,'somekey2').content.decode())
        expected = {
            'valid': 'Key validated.'
        }
        self.assertDictEqual(out,expected)
        r = self.factory.get('/api/verify/somekey2sdadfsdaf')
        out = json.loads(verify(r,'somekey2sadfsadfsaf').content.decode())
        expected = {
            'error': 'Invalid key provided.'
        }
        self.assertDictEqual(out,expected)
        r = self.factory.get('/api/verify/')
        out = json.loads(verify(r,None).content.decode())
        expected = {
            'error': 'No API key provided.'
        }
        self.assertDictEqual(out,expected)

    def test_mod_details(self):
        from .views import mod
        r = self.factory.get('/api/mod/mod/')
        out = json.loads(mod(r,'mod').content.decode())
        expected = {
            'name': 'mod',
            'link': 'http://nope.org',
            'author': 'me',
            'versions': ['1.0', '1.2'],
            'pretty_name': 'pretty_mod',
            'description': 'mod_d'
        }
        self.assertDictEqual(out,expected)

class ViewHTMLTest(DTest):
    @classmethod
    def setUpClass(cls):
        cls.factory = RequestFactory()
        ApiKey(key='testkey',description='mykey').save()
        ApiKey(key='testkey2',description='mykey').save()

    def test_apikeys_manage(self):
        from .views import apikeys_manage
        r = self.factory.get('/') # out of fucks to give, sorry
        out = apikeys_manage(r)
        self.assertTemplateUsed(out,'api/manage.html')
        self.assertContains(out,'testkey')
        self.assertContains(out,'testkey2')
        r = self.factory.post('/')
        key = ApiKey.objects.filter(key='testkey').first()
        r.POST = {
            'deletekey' : key.id
        }
        apikeys_manage(r)
        self.assertTrue(len(ApiKey.objects.filter(key='testkey')) == 0)
        r = self.factory.post('/')
        r.POST = {
            'addkey' : 'testkey',
            'keydesc' : 'mykey'
        }
        apikeys_manage(r)
        keys = ApiKey.objects.filter(key='testkey')
        print(keys)
        self.assertTrue(len(keys) == 1)
        key = keys.first()
        self.assertEqual(key.key, 'testkey')
        self.assertEqual(key.description, 'mykey')
