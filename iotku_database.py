from pymongo import MongoClient
import hashlib, datetime

class Iotku:
	def __init__(
					self,
					client = MongoClient(),
					db = 'iotku',
					user_list = 'user_list',
					device_list = 'device_list',
					sensor_list = 'sensor_list'
				):
		self.client = client
		self.db = self.client[db]
		self.user_list = self.db[user_list]
		self.device_list = self.db[device_list]
		self.sensor_list = self.db[sensor_list]
		
	def get_user_list(self):
		return_list = [x for x in self.user_list.find({})]
		return return_list
		
	def find_user(self, **user_info):
		result = self.user_list.find_one(user_info)
		if result:
			_id = result["_id"]
			return User(_id, self.user_list, self.device_list, self.sensor_list)
		else:
			return None
		
	def add_user(self, **doc):
		doc["api_key"] = hashlib.md5(doc["email"].encode('utf-8')).hexdigest()
		doc["device_list"] = []
		inserted = self.user_list.insert_one(doc)
		_id = inserted.inserted_id
		return User(_id, self.user_list, self.device_list, self.sensor_list)

	
class User(Iotku):
	def __init__(self, _id, user_list, device_list, sensor_list):
		self.user_list = user_list
		self.device_list = device_list
		self.sensor_list = sensor_list
		
		self._id = _id
		self.user_document = self.user_list.find_one({"_id":self._id})
		self.email = self.user_document["email"]
		self.api_key = self.user_document["api_key"]
		self.password = self.user_document["password"]
		
	def reload(self):
		self.__init__(self._id, self.user_list, self.device_list, self.sensor_list)
		return True
		
	def change_user_info(self, **kwargs):
		user_info = kwargs
		for key, value in user_info.iteritems():
			self.user_document[key] = value
		self.user_list.save(self.user_document)
		self.reload()
		return True
		
	def get_device_list(self):
		device_list = [x["device_ip"] for x in self.user_document["device_list"]]
		return device_list

	def add_device(self, device_ip, device_name):
		date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		mongo_id = self.device_list.insert_one({"device_name":device_name, "device_ip":device_ip,"time_added":date,"sensor_list":[]})
		_id = mongo_id.inserted_id
		self.user_document["device_list"].append({"device_ip":device_ip,"mongo_id":_id})
		self.user_list.save(self.user_document)
		return Device(_id, self.device_list, self.sensor_list)
		
	def remove_device(self, device_ip):
		device_info = next((item for item in self.user_document["device_list"] if item["device_ip"] == device_ip), False)
		if device_info:
			self.device_list.remove_one({"_id":device_info["mongo_id"]})
			self.user_document["device_list"].remove(device_info)
			self.user_list.save(self.user_document)
			return True
		else:
			return False
			
	def find_device(self, device_ip):
		device_info = next((item for item in self.user_document["device_list"] if item["device_ip"] == device_ip), False)
		if device_info:
			result = self.device_list.find_one({"_id":device_info["mongo_id"]})
			_id = result["_id"]
			return Device(_id, self.device_list, self.sensor_list)
		else:
			return False
			
class Device(User):
	def __init__(self, _id, device_list, sensor_list):
		self.device_list = device_list
		self.sensor_list = sensor_list
		self._id = _id
		self.device_document = self.device_list.find_one({"_id":self._id})
		self.device_name = self.device_document["device_name"]
		self.device_ip = self.device_document["device_ip"]
		self.time_added = self.device_document["time_added"]
		
	def reload(self):
		self.__init__(self._id)
		return True
		
	def change_device_info(self, **device_info):
		for key, value in device_info.iteritems():
			self.device_document[key] = value
		self.device_list.save(self.device_document)
		self.reload()
		return True
		
	def get_sensor_list(self):
		sensor_list = self.device_document["sensor_list"]
		return sensor_list
		
	def add_sensor(self, sensor_id, sensor_name):
		date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		mongo_id = self.sensor_list.insert_one({"sensor_id":sensor_id, "sensor_name":sensor_name,"time_added":date,"last_data_added_time":"","total_data_entry":0,"data_collection":[]})
		_id = mongo_id.inserted_id
		self.device_document["sensor_list"].append({"sensor_id":sensor_id,"mongo_id":_id})
		self.device_list.save(self.device_document)
		return Sensor(_id, self.sensor_list)
		
	def remove_sensor(self, sensor_id):
		sensor_info = next((item for item in self.device_document["device_list"] if item["sensor_id"] == sensor_id), False)
		if sensor_info:
			self.sensor_list.remove_one({"_id":sensor_info["mongo_id"]})
			self.device_document["sensor_list"].remove(sensor_info)
			self.device_list.save(self.device_document)
			return True
		else:
			return False
			
	def find_sensor(self,sensor_id):
		sensor_info = next((item for item in self.device_document["sensor_list"] if item["sensor_id"] == sensor_id), False)
		if sensor_info:
			result = self.sensor_list.find_one({"_id":sensor_info["mongo_id"]})
			_id = result["_id"]
			return Sensor(_id, self.sensor_list)
		else:
			return False
	
class Sensor(Device):
	def __init__(self, _id, sensor_list):
		self.sensor_list = sensor_list
		self._id = _id
		self.sensor_document = self.sensor_list.find_one({"_id":self._id})
		self.sensor_name = self.sensor_document["sensor_name"]
		self.time_added = self.sensor_document["time_added"]
		self.last_data_added_time = self.sensor_document["last_data_added_time"]
		self.total_data_entry = self.sensor_document["total_data_entry"]
		
	def reload(self):
		self.__init__(self._id,self.sensor_list)
		return True
		
	def change_sensor_info(self, **sensor_info):
		for key, value in device_info.iteritems():
			self.sensor_document[key] = value
		self.sensor_list.save(self.sensor_document)
		self.reload()
		return True
		
	def post_data(self, data_value):
		date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		data_entry = {"time_added":date,"data_value":data_value}
		self.sensor_document["data_collection"].append(data_entry)
		self.sensor_list.save(self.sensor_document)
		
	def get_data(self, get_from=0, to=-1):
		data_list = self.sensor_document["data_collection"].sort(key=lambda item:item['time_added'], reverse=True)
		return data_list[get_from:to]
		