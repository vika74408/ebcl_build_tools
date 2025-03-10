from ebcl.tools.secure_aptrepo.secure_repo import Server
import os
import shutil
import tempfile
import pytest

from ebcl.common.fake import Fake
from ebcl.tools.root.root import RootGenerator
from ebcl.tools.initrd.initrd import InitrdGenerator


class TestCredential:

    yaml: str
    temp_dir: str
    server: Server
    repo_dir: str
    fake: Fake
    data_dir: str
    passwd: str

    @classmethod
    def setup_class(cls):
        cls.fake = Fake()
        tmp = os.path.join(os.path.dirname(__file__), 'data')
        cls.yaml = os.path.join(tmp, 'repo_local.yaml')
        cls.repo_dir = '/workspace/results/packages/'
        cls.data_dir = os.path.join(tmp, 'flat_repo/')
        cls.passwd = '/workspace/tools/user_config/auth.d/localrepo.conf'

        # setup basic repo
        cls.fake.run_cmd(f'{cls.data_dir}/credential_repo_setup {cls.data_dir}')

        cls.server = Server(port=8088, username='ebcl', password='ebcl', directory=cls.repo_dir)
        cls.server.start()
        cls.temp_dir = tempfile.mkdtemp()

    @classmethod
    def teardown_class(cls):
        cls.server.stop()
        shutil.rmtree(cls.temp_dir)
        cls.fake.run_cmd(f'rm -fr {cls.repo_dir}/*')

    def test_auth_rootfs(self):
        print("basic rootfs creation with credential's protected apt repo")
        self.fake.run_cmd(f'install -m 600 {self.data_dir}/auth.d/good.conf {self.passwd}')
        self.fake.run_cmd('rm -fr /workspace/state/*')

        generator = RootGenerator(self.yaml, self.temp_dir, False)
        archive = None
        archive = generator.create_root()
        assert archive
        assert os.path.isfile(archive)

    def test_auth_initrd(self):
        print("basic initrd creation with credential's protected apt repo")
        self.fake.run_cmd(f'install -m 600 {self.data_dir}/auth.d/good.conf {self.passwd}')
        self.fake.run_cmd('rm -fr /workspace/state/*')

        initrd = InitrdGenerator(self.yaml, self.temp_dir)
        image = None
        image = initrd.create_initrd()
        assert image
        assert os.path.isfile(os.path.join(
            initrd.target_dir, 'bin', 'busybox'))
        # just for testing ebcl-doc is made it as amd64 instead of all
        assert os.path.isfile(os.path.join(
            initrd.target_dir, 'usr', 'share', 'ebcl-doc', 'ebcl_doc.txt'))

    @pytest.mark.skip(reason="credential negative tests are skipped to avoid unwanted delays ")
    def test_auth_rootfs_neg(self):
        print("negative: basic rootfs creation with credential's protected apt repo")
        self.fake.run_cmd(f'install -m 600 {self.data_dir}/auth.d/wrong.conf {self.passwd}')
        self.fake.run_cmd('rm -fr /workspace/state/*')

        generator = RootGenerator(self.yaml, self.temp_dir, False)
        archive = None
        archive = generator.create_root()
        assert archive is None

    @pytest.mark.skip(reason="credential negative tests are skipped to avoid unwanted delays ")
    def test_auth_initrd_neg(self):
        print("negative: basic initrd creation with credential's protected apt repo")
        self.fake.run_cmd(f'install -m 600 {self.data_dir}/auth.d/wrong.conf {self.passwd}')
        self.fake.run_cmd('rm -fr /workspace/state/*')

        initrd = InitrdGenerator(self.yaml, self.temp_dir)
        image = None
        image = initrd.create_initrd()
        assert image is None

    @pytest.mark.skip(reason="credential negative tests are skipped to avoid unwanted delays ")
    def test_apt_http_connection_neg(self):
        print("negative: apt with credential: https/http missing in auth files")
        self.fake.run_cmd(f'install -m 600 {self.data_dir}/auth.d/without_http.conf {self.passwd}')
        self.fake.run_cmd('rm -fr /workspace/state/*')

        generator = RootGenerator(self.yaml, self.temp_dir, False)
        archive = None
        archive = generator.create_root()
        assert archive is None
