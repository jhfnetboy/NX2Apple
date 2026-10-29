"""Stripped Unity 5.6 Shader resources, without game data (Guns, Gore & Cannoli 2's layout)."""
from pathlib import Path
import struct
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import unityfs

TYPE_HASH = bytes.fromhex('a70f7abc6586fb35b3a0641aa81e9375')


def string(value):
    raw = value.encode()
    return struct.pack('<i', len(raw)) + raw + bytes(-len(raw) % 4)


class Unity56Tests(unittest.TestCase):
    def test_stripped_shader_before_2019_3(self):
        # The 5.6 Shader: name, parsed form (empty properties, one subshader with no passes, no tags, LOD 0, three empty strings, no dependencies),
        # then one platform with the pre-2019.3 single segment per platform (a plain number, not an array), an empty blob and a dependency, aligned baked flag
        parsed = (struct.pack('<i', 0)                                   # m_PropInfo.m_Props
                  + struct.pack('<i', 1)                                 # m_SubShaders: one
                  + struct.pack('<i', 0) + struct.pack('<i', 0) + struct.pack('<i', 0)   # its passes, tags, LOD
                  + string('Legacy/Blit') + string('') + string('')      # m_Name, custom editor, fallback
                  + struct.pack('<i', 0)                                 # m_Dependencies
                  + b'\1\0\0\0')                                         # m_DisableNoSubshadersMessage (aligned)
        arrays = (struct.pack('<iI', 1, 38) + struct.pack('<iI', 1, 0)    # platforms, offsets
                  + struct.pack('<iI', 1, 0) + struct.pack('<iI', 1, 0)   # compressedLengths, decompressedLengths
                  + struct.pack('<i', 0))                                 # compressedBlob
        payload = (string('Legacy') + parsed + arrays
                   + struct.pack('<i', 1) + struct.pack('<iq', 0, 42)     # one m_Platform dependency
                   + b'\1\0\0\0')                                         # m_ShaderIsBaked
        metadata = (b'5.6.6f2\0' + struct.pack('<i?iiBh', 38, False, 1, 48, 0, -1) + TYPE_HASH + struct.pack('<i', 1))
        metadata += bytes(-(20 + len(metadata)) % 4)
        metadata += struct.pack('<qIII', 1, 0, len(payload), 0)
        data = (struct.pack('>IIII', len(metadata), 0x100 + len(payload), 17, 0x100) + bytes(4) + metadata).ljust(0x100, b'\0') + payload
        tree = unityfs.known_tree(48, TYPE_HASH)
        shader = list(unityfs.serialized_objects(data, {}, {48}, {(48, TYPE_HASH): tree}))[0][2]
        self.assertEqual(shader['m_ParsedForm']['m_Name'], 'Legacy/Blit')
        self.assertEqual(shader['platforms'], [38])
        self.assertEqual(shader['offsets'], [0])
        self.assertEqual(len(shader['m_ParsedForm']['m_SubShaders']), 1)
        self.assertEqual(shader['m_Dependencies'], [{'m_FileID': 0, 'm_PathID': 42}])
        self.assertTrue(shader['m_ShaderIsBaked'])
        reader = unityfs.Reader(payload, True)
        unityfs._read(reader, tree)
        self.assertEqual(reader.p, len(payload))

    def test_layout_is_the_5_6_one(self):
        # Field for field: the 5.6 Shader keeps one segment per platform (a number) and has neither m_NonModifiableTextures nor the newer per-subprogram fields
        tree = unityfs.known_tree(48, TYPE_HASH)
        fields = [kid.name for kid in tree.kids]
        self.assertEqual(fields, ['m_Name', 'm_ParsedForm', 'platforms', 'offsets', 'compressedLengths',
                                  'decompressedLengths', 'compressedBlob', 'm_Dependencies', 'm_ShaderIsBaked'])
        parsed = {kid.name: kid for kid in tree.kids}
        sub = {kid.name: kid for kid in parsed['m_ParsedForm'].kids}
        self.assertEqual(sub['m_SubShaders'].kids[0].kids[1].type, 'SerializedSubShader')   # the Array is unaligned in 5.6
        self.assertEqual(sub['m_SubShaders'].kids[0].kids[1].flags, 0)
        self.assertEqual([kid.name for kid in sub['m_SubShaders'].kids[0].kids[1].kids], ['m_Passes', 'm_Tags', 'm_LOD'])


if __name__ == '__main__':
    unittest.main()
