import io
import os
import tempfile
import unittest
from collections import OrderedDict
from datetime import datetime

import six
from mock import patch
import cloudinary
from cloudinary import api, uploader, utils

from urllib3 import disable_warnings
from urllib3.util import parse_url
from test.helper_test import uploader_response_mock, SUFFIX, TEST_IMAGE, get_params, TEST_ICON, TEST_DOC, \
    REMOTE_TEST_IMAGE, UTC

MOCK_RESPONSE = uploader_response_mock()

TEST_IMAGE_HEIGHT = 51
TEST_IMAGE_WIDTH = 241

TEST_TRANS_OVERLAY = {"font_family": "arial", "font_size": 20, "text": SUFFIX}
TEST_TRANS_OVERLAY_STR = "text:arial_20:{}".format(SUFFIX)

TEST_TRANS_SCALE2 = dict(crop="scale", width="2.0", overlay=TEST_TRANS_OVERLAY_STR)
TEST_TRANS_SCALE2_STR = "c_scale,l_{},w_2.0".format(TEST_TRANS_OVERLAY_STR)

TEST_TRANS_SCALE2_PNG = dict(crop="scale", width="2.0", format="png", overlay=TEST_TRANS_OVERLAY_STR)
TEST_TRANS_SCALE2_PNG_STR = "c_scale,l_{},w_2.0/png".format(TEST_TRANS_OVERLAY_STR)

UNIQUE_TAG = "up_test_uploader_{}".format(SUFFIX)
TEST_DOCX_ID = "test_docx_{}".format(SUFFIX)
TEXT_ID = "text_{}".format(SUFFIX)
TEST_ID1 = "uploader_test_{}".format(SUFFIX)
TEST_ID2 = "uploader_test_{}2".format(SUFFIX)

disable_warnings()


class UploaderTest(unittest.TestCase):

    def setUp(self):
        cloudinary.reset_config()

    @classmethod
    def tearDownClass(cls):
        cloudinary.api.delete_resources_by_tag(UNIQUE_TAG)
        cloudinary.api.delete_resources_by_tag(UNIQUE_TAG, resource_type='raw')
        cloudinary.api.delete_resources_by_tag(UNIQUE_TAG, type='twitter_name')
        cloudinary.api.delete_resources([TEST_ID1, TEST_ID2])
        cloudinary.api.delete_resources([TEXT_ID], type='text')
        cloudinary.api.delete_resources([TEST_DOCX_ID], resource_type='raw')

        for trans in [TEST_TRANS_SCALE2_STR, TEST_TRANS_SCALE2_PNG_STR]:
            try:
                api.delete_transformation(trans)
            except Exception:
                pass

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload(self):
        """should successfully upload file """
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(
            dict(public_id=result["public_id"], version=result["version"]),
            cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_file_io_without_filename(self):
        """should successfully upload FileIO file """
        with io.BytesIO() as temp_file, \
                open(TEST_IMAGE, 'rb') as input_file:
            temp_file.write(input_file.read())
            temp_file.seek(0)
            result = uploader.upload(temp_file, tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        self.assertEqual('stream', result["original_filename"])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_async(self, mocker):
        """should pass async value """
        mocker.return_value = MOCK_RESPONSE
        uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], async=True)
        params = mocker.call_args[0][2]
        self.assertTrue(params['async'])

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_ocr(self, mocker):
        """should pass ocr value """
        mocker.return_value = MOCK_RESPONSE
        uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG], ocr='adv_ocr')
        args, kargs = mocker.call_args
        self.assertEqual(get_params(args)['ocr'], 'adv_ocr')

    @patch('urllib3.request.RequestMethods.request')
    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_quality_override(self, mocker):
        """should pass quality_override """
        mocker.return_value = MOCK_RESPONSE
        test_values = ['auto:advanced', 'auto:best', '80:420', 'none']
        for quality in test_values:
            uploader.upload(TEST_IMAGE, tags=UNIQUE_TAG, quality_override=quality)
            params = mocker.call_args[0][2]
            self.assertEqual(params['quality_override'], quality)
        # verify explicit works too
        uploader.explicit(TEST_IMAGE, quality_override='auto:best')
        params = mocker.call_args[0][2]
        self.assertEqual(params['quality_override'], 'auto:best')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_url(self):
        """should successfully upload file by url """
        result = uploader.upload(REMOTE_TEST_IMAGE, tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(
            dict(public_id=result["public_id"], version=result["version"]),
            cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_unicode_url(self):
        """should successfully upload file by unicode url """
        unicode_image_url = u"{}".format(REMOTE_TEST_IMAGE)
        result = uploader.upload(unicode_image_url, tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(result["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(
            dict(public_id=result["public_id"], version=result["version"]),
            cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_data_uri(self):
        """should successfully upload file by data url """
        result = uploader.upload(
            u"""\
data:image/png;base64,iVBORw0KGgoAA
AANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAABlBMVEUAAAD///+l2Z/dAAAAM0l
EQVR4nGP4/5/h/1+G/58ZDrAz3D/McH8yw83NDDeNGe4Ug9C9zwz3gVLMDA/A6
P9/AFGGFyjOXZtQAAAAAElFTkSuQmCC\
""",
            tags=[UNIQUE_TAG])
        self.assertEqual(result["width"], 16)
        self.assertEqual(result["height"], 16)
        expected_signature = utils.api_sign_request(
            dict(public_id=result["public_id"], version=result["version"]),
            cloudinary.config().api_secret)
        self.assertEqual(result["signature"], expected_signature)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_rename(self):
        """should successfully rename a file"""
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        uploader.rename(result["public_id"], result["public_id"]+"2")
        self.assertIsNotNone(api.resource(result["public_id"]+"2"))
        result2 = uploader.upload(TEST_ICON, tags=[UNIQUE_TAG])
        self.assertRaises(api.Error, uploader.rename,
                          result2["public_id"], result["public_id"]+"2")
        uploader.rename(result2["public_id"], result["public_id"]+"2", overwrite=True)
        self.assertEqual(api.resource(result["public_id"]+"2")["format"], "ico")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_use_filename(self):
        """should successfully take use file name of uploaded file in public id if specified use_filename """
        result = uploader.upload(TEST_IMAGE, use_filename=True, tags=[UNIQUE_TAG])
        six.assertRegex(self, result["public_id"], 'logo_[a-z0-9]{6}')
        result = uploader.upload(
            TEST_IMAGE, use_filename=True, unique_filename=False, tags=[UNIQUE_TAG])
        self.assertEqual(result["public_id"], 'logo')

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_explicit(self):
        """should support explicit """
        result = uploader.explicit("cloudinary", type="twitter_name", eager=[TEST_TRANS_SCALE2_PNG], tags=[UNIQUE_TAG])
        params = dict(TEST_TRANS_SCALE2_PNG, type="twitter_name", version=result["version"])
        url = utils.cloudinary_url("cloudinary", **params)[0]
        actual = result["eager"][0]["url"]
        self.assertEqual(parse_url(actual).path, parse_url(url).path)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_eager(self):
        """should support eager """
        uploader.upload(TEST_IMAGE, eager=[TEST_TRANS_SCALE2], tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_header(self):
        """should support headers """
        uploader.upload(TEST_IMAGE, headers=["Link: 1"], tags=[UNIQUE_TAG])
        uploader.upload(TEST_IMAGE, headers={"Link": "1"}, tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_text(self):
        """should successfully generate text image """
        result = uploader.text("hello world", public_id=TEXT_ID)
        self.assertGreater(result["width"], 1)
        self.assertGreater(result["height"], 1)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_tags(self):
        """should successfully upload file """
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        result2 = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        uploader.add_tag("tag1", [result["public_id"], result2["public_id"]])
        uploader.add_tag("tag2", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag1", "tag2", UNIQUE_TAG])
        self.assertEqual(api.resource(result2["public_id"])["tags"], ["tag1", UNIQUE_TAG])
        uploader.remove_tag("tag1", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag2", UNIQUE_TAG])
        uploader.replace_tag("tag3", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag3"])
        uploader.replace_tag(UNIQUE_TAG, result["public_id"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_remove_all_tags(self):
        """should successfully remove all tags"""
        result = uploader.upload(TEST_IMAGE, public_id=TEST_ID1)
        result2 = uploader.upload(TEST_IMAGE, public_id=TEST_ID2)
        uploader.add_tag("tag1", [result["public_id"], result2["public_id"]])
        uploader.add_tag("tag2", result["public_id"])
        self.assertEqual(api.resource(result["public_id"])["tags"], ["tag1", "tag2"])
        self.assertEqual(api.resource(result2["public_id"])["tags"], ["tag1"])
        uploader.remove_all_tags([result["public_id"], result2["public_id"]])
        self.assertFalse("tags" in api.resource(result["public_id"]))
        self.assertFalse("tags" in api.resource(result2["public_id"]))

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats(self):
        """ should allow whitelisted formats if allowed_formats """
        result = uploader.upload(TEST_IMAGE, allowed_formats=['png'], tags=[UNIQUE_TAG])
        self.assertEqual(result["format"], "png")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_illegal_format(self):
        """should prevent non whitelisted formats from being uploaded if allowed_formats is specified"""
        self.assertRaises(api.Error, uploader.upload, TEST_IMAGE, allowed_formats=['jpg'])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_allowed_formats_with_format(self):
        """should allow non whitelisted formats if type is specified and convert to that type"""
        result = uploader.upload(TEST_IMAGE, allowed_formats=['jpg'], format='jpg', tags=[UNIQUE_TAG])
        self.assertEqual("jpg", result["format"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_face_coordinates(self):
        """should allow sending face coordinates"""
        coordinates = [[120, 30, 109, 150], [121, 31, 110, 151]]
        result_coordinates = [[120, 30, 109, 51], [121, 31, 110, 51]]
        result = uploader.upload(TEST_IMAGE, face_coordinates=coordinates,
                                 faces=True, tags=[UNIQUE_TAG])
        self.assertEqual(result_coordinates, result["faces"])

        different_coordinates = [[122, 32, 111, 152]]
        custom_coordinates = [1, 2, 3, 4]
        uploader.explicit(result["public_id"], face_coordinates=different_coordinates,
                          custom_coordinates=custom_coordinates, type="upload")
        info = api.resource(result["public_id"], faces=True, coordinates=True)
        self.assertEqual(different_coordinates, info["faces"])
        self.assertEqual({"faces": different_coordinates, "custom": [custom_coordinates]}, info["coordinates"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_context(self):
        """should allow sending context"""
        context = {"caption": "some caption", "alt": "alternative|alt=a"}
        result = uploader.upload(TEST_IMAGE, context=context, tags=[UNIQUE_TAG])
        info = api.resource(result["public_id"], context=True)
        self.assertEqual({"custom": context}, info["context"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_add_context(self):
        """should allow adding context"""
        context = {"caption": "some caption", "alt": "alternative|alt=a"}
        result = uploader.upload(TEST_IMAGE, tags=[UNIQUE_TAG])
        info = api.resource(result["public_id"], context=True)
        self.assertFalse("context" in info)
        uploader.add_context(context, result["public_id"])
        info = api.resource(result["public_id"], context=True)
        self.assertEqual({"custom": context}, info["context"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_remove_all_context(self):
        """should allow removing all context"""
        context = {"caption": "some caption", "alt": "alternative|alt=a"}
        result = uploader.upload(TEST_IMAGE, context=context, tags=[UNIQUE_TAG])
        info = api.resource(result["public_id"], context=True)
        self.assertEqual({"custom": context}, info["context"])
        uploader.remove_all_context(result["public_id"])
        info = api.resource(result["public_id"], context=True)
        self.assertFalse("context" in info)

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_manual_moderation(self):
        """ should support setting manual moderation status """
        resource = uploader.upload(TEST_IMAGE, moderation="manual", tags=[UNIQUE_TAG])

        self.assertEqual(resource["moderation"][0]["status"], "pending")
        self.assertEqual(resource["moderation"][0]["kind"], "manual")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_raw_conversion(self):
        """ should support requesting raw_convert """
        with six.assertRaisesRegex(self, api.Error, 'Raw convert is invalid'):
            uploader.upload(TEST_DOC, public_id=TEST_DOCX_ID, raw_convert="illegal",
                            resource_type="raw", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_categorization(self):
        """ should support requesting categorization """
        with six.assertRaisesRegex(self, api.Error, 'is not valid'):
            uploader.upload(TEST_IMAGE, categorization="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_detection(self):
        """ should support requesting detection """
        with six.assertRaisesRegex(self, api.Error, 'illegal is not a valid'):
            uploader.upload(TEST_IMAGE, detection="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_large(self):
        """ should support uploading large files """
        temp_file = tempfile.NamedTemporaryFile()
        temp_file_name = temp_file.name
        temp_file.write(b"BMJ\xB9Y\x00\x00\x00\x00\x00\x8A\x00\x00\x00|\x00\x00\x00x\x05\x00\x00x\x05\x00\x00\x01\
\x00\x18\x00\x00\x00\x00\x00\xC0\xB8Y\x00a\x0F\x00\x00a\x0F\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\x00\
\x00\xFF\x00\x00\xFF\x00\x00\x00\x00\x00\x00\xFFBGRs\x00\x00\x00\x00\x00\x00\x00\x00T\xB8\x1E\xFC\x00\x00\x00\x00\
\x00\x00\x00\x00fff\xFC\x00\x00\x00\x00\x00\x00\x00\x00\xC4\xF5(\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        for i in range(0, 588000):
            temp_file.write(b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF")

        temp_file.flush()
        self.assertEqual(5880138, os.path.getsize(temp_file_name))

        resource = uploader.upload_large(temp_file_name, chunk_size=5243000, tags=["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource["tags"], ["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource["resource_type"], "raw")

        resource2 = uploader.upload_large(temp_file_name, chunk_size=5243000, tags=["upload_large_tag", UNIQUE_TAG],
                                          resource_type="image")
        self.assertEqual(resource2["tags"], ["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource2["resource_type"], "image")
        self.assertEqual(resource2["width"], 1400)
        self.assertEqual(resource2["height"], 1400)

        resource3 = uploader.upload_large(temp_file_name, chunk_size=5880138, tags=["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource3["tags"], ["upload_large_tag", UNIQUE_TAG])
        self.assertEqual(resource3["resource_type"], "raw")

        # should allow fallback of upload large with remote url to regular upload
        resource4 = uploader.upload_large(REMOTE_TEST_IMAGE, tags=[UNIQUE_TAG])
        self.assertEqual(resource4["width"], TEST_IMAGE_WIDTH)
        self.assertEqual(resource4["height"], TEST_IMAGE_HEIGHT)
        expected_signature = utils.api_sign_request(dict(public_id=resource4["public_id"],
                                                         version=resource4["version"]),
                                                    cloudinary.config().api_secret)
        self.assertEqual(resource4["signature"], expected_signature)

        temp_file.close()

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_preset(self):
        """ should support unsigned uploading using presets """
        preset = api.create_upload_preset(folder="upload_folder", unsigned=True, tags=[UNIQUE_TAG])
        result = uploader.unsigned_upload(TEST_IMAGE, preset["name"], tags=[UNIQUE_TAG])
        six.assertRegex(self, result["public_id"], r'^upload_folder\/[a-z0-9]+$')
        api.delete_upload_preset(preset["name"])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_background_removal(self):
        """ should support requesting background_removal """
        with six.assertRaisesRegex(self, api.Error, 'is invalid'):
            uploader.upload(TEST_IMAGE, background_removal="illegal", tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_upload_timeout(self):
        with six.assertRaisesRegex(self, cloudinary.api.Error, 'timed out'):
            uploader.upload(TEST_IMAGE, timeout=0.001, tags=[UNIQUE_TAG])

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    def test_responsive_breakpoints(self):
        result = uploader.upload(
            TEST_IMAGE,
            tags=[UNIQUE_TAG],
            responsive_breakpoints=dict(create_derived=False,
                                        transformation=dict(angle=90)))

        self.assertIsNotNone(result["responsive_breakpoints"])
        self.assertEqual(result["responsive_breakpoints"][0]["transformation"],
                         "a_90")

        result = uploader.explicit(
            result["public_id"],
            type="upload",
            tags=[UNIQUE_TAG],
            responsive_breakpoints=[dict(create_derived=False,
                                         transformation=dict(angle=90)),
                                    dict(create_derived=False,
                                         transformation=dict(angle=45))])

        self.assertIsNotNone(result["responsive_breakpoints"])
        self.assertEqual(result["responsive_breakpoints"][0]["transformation"],
                         "a_90")
        self.assertEqual(result["responsive_breakpoints"][1]["transformation"],
                         "a_45")

    @unittest.skipUnless(cloudinary.config().api_secret, "requires api_key/api_secret")
    @patch('urllib3.request.RequestMethods.request')
    def test_access_control(self, request_mock):
        request_mock.return_value = MOCK_RESPONSE

        # Should accept a dictionary of strings
        acl = OrderedDict((("access_type", "anonymous"),
                          ("start", "2018-02-22 16:20:57 +0200"),
                          ("end", "2018-03-22 00:00 +0200")))
        exp_acl = '[{"access_type":"anonymous","start":"2018-02-22 16:20:57 +0200","end":"2018-03-22 00:00 +0200"}]'

        uploader.upload(TEST_IMAGE, access_control=acl)
        params = get_params(request_mock.call_args[0])

        self.assertIn("access_control", params)
        self.assertEqual(exp_acl, params["access_control"])

        # Should accept a dictionary of datetime objects
        acl_2 = OrderedDict((("access_type", "anonymous"),
                            ("start", datetime.strptime("2019-02-22 16:20:57Z", "%Y-%m-%d %H:%M:%SZ")),
                            ("end", datetime(2019, 3, 22, 0, 0, tzinfo=UTC()))))

        exp_acl_2 = '[{"access_type":"anonymous","start":"2019-02-22T16:20:57","end":"2019-03-22T00:00:00+00:00"}]'

        uploader.upload(TEST_IMAGE, access_control=acl_2)
        params = get_params(request_mock.call_args[0])

        self.assertEqual(exp_acl_2, params["access_control"])

        # Should accept a JSON string
        acl_str = '{"access_type":"anonymous","start":"2019-02-22 16:20:57 +0200","end":"2019-03-22 00:00 +0200"}'
        exp_acl_str = '[{"access_type":"anonymous","start":"2019-02-22 16:20:57 +0200","end":"2019-03-22 00:00 +0200"}]'

        uploader.upload(TEST_IMAGE, access_control=acl_str)
        params = get_params(request_mock.call_args[0])

        self.assertEqual(exp_acl_str, params["access_control"])

        # Should accept a list of all the above values
        list_of_acl = [acl, acl_2, acl_str]
        # Remove starting "[" and ending "]" in all expected strings and combine them into one string
        expected_list_of_acl = "[" + ",".join([v[1:-1] for v in(exp_acl, exp_acl_2, exp_acl_str)]) + "]"

        uploader.upload(TEST_IMAGE, access_control=list_of_acl)
        params = get_params(request_mock.call_args[0])

        self.assertEqual(expected_list_of_acl, params["access_control"])

        # Should raise ValueError on invalid values
        invalid_values = [[[]], ["not_a_dict"], [7357]]
        for invalid_value in invalid_values:
            with self.assertRaises(ValueError):
                uploader.upload(TEST_IMAGE, access_control=invalid_value)


if __name__ == '__main__':
    unittest.main()
