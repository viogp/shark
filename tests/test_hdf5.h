//
// HDF5 simple unit tests
//
// ICRAR - International Centre for Radio Astronomy Research
// (c) UWA - The University of Western Australia, 2018
// Copyright by UWA (in the framework of the ICRAR)
// All rights reserved
//
// This library is free software; you can redistribute it and/or
// modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation; either
// version 2.1 of the License, or (at your option) any later version.
//
// This library is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public
// License along with this library; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston,
// MA 02111-1307  USA
//

#include <cxxtest/TestSuite.h>

#include <boost/filesystem.hpp>
#include "hdf5/reader.h"
#include "hdf5/writer.h"

using namespace shark;
namespace fs = boost::filesystem;

class TestHDF5 : public CxxTest::TestSuite {

private:
	hdf5::Writer get_writer()
	{
		return hdf5::Writer("test.hdf5");
	}

	hdf5::Reader get_reader()
	{
		return hdf5::Reader("test.hdf5");
	}

public:

	virtual void tearDown() {
		fs::path path("test.hdf5");
		if (fs::exists(path)) {
			fs::remove(path);
		}
	}

	void test_write_dataset_scalars()
	{
		// Reference data
		int an_integer = 1;
		float a_float = 1;
		double a_double = 1;

		// Write first
		{
			auto writer = get_writer();
			writer.write_dataset("integer", an_integer);
			writer.write_dataset("float", a_float);
			writer.write_dataset("double", a_double);
		}

		// Read and verify
		auto reader = get_reader();
		auto hdf5_integer = reader.read_dataset<int>("integer");
		auto hdf5_float = reader.read_dataset<float>("float");
		auto hdf5_double = reader.read_dataset<double>("double");

		TS_ASSERT_EQUALS(an_integer, hdf5_integer);
		TS_ASSERT_EQUALS(a_float, hdf5_float);
		TS_ASSERT_EQUALS(a_double, hdf5_double);
	}

	void test_write_dataset_vectors()
	{
		// Reference data
		std::vector<int> integers {1, 2, 3, 4};
		std::vector<float> floats {1, 2, 3, 4};
		std::vector<double> doubles {1, 2, 3, 4};

		// Write first
		{
			auto writer = get_writer();
			writer.write_dataset("integers", integers);
			writer.write_dataset("floats", floats);
			writer.write_dataset("doubles", doubles);
		}

		// Read and verify
		auto reader = get_reader();
		auto hdf5_integers = reader.read_dataset_v<int>("integers");
		auto hdf5_floats = reader.read_dataset_v<float>("floats");
		auto hdf5_doubles = reader.read_dataset_v<double>("doubles");

		TS_ASSERT_EQUALS(integers, hdf5_integers);
		TS_ASSERT_EQUALS(floats, hdf5_floats);
		TS_ASSERT_EQUALS(doubles, hdf5_doubles);
	}

	void test_wrong_attribute_writes()
	{
		// Single-named attributes are not supported
		auto writer = get_writer();
		TS_ASSERT_THROWS(writer.write_attribute("/attr_name", 1), invalid_argument);
		TS_ASSERT_THROWS(writer.write_attribute("/attr_name", std::string("1")), invalid_argument);
	}

	template <typename T>
	void _test_attribute_writes(const T &val)
	{
		// Write/read an attribute both in a dataset and in a group
		{
			auto writer = get_writer();
			writer.write_dataset("/group/integers", std::vector<int>{1, 2, 3, 4});
			writer.write_attribute("/group/attribute", val);
			writer.write_attribute("/group/integers/attribute", val);
		}

		auto reader = get_reader();
		TS_ASSERT_EQUALS(reader.read_attribute<T>("/group/attribute"), val);
		TS_ASSERT_EQUALS(reader.read_attribute<T>("/group/integers/attribute"), val);
	}

	void test_attribute_writes()
	{
		_test_attribute_writes(1);
//		_test_attribute_writes(1.f);
//		_test_attribute_writes(1.);
	}

};