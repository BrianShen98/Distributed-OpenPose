def processImage(image_with_id):
  import sys
  sys.path.append("/usr/local/python")
  from openpose import pyopenpose as op
  
  params = dict()
  params["model_folder"] = "/usr/local/openpose/models/"

  # Starting OpenPose
  opWrapper = op.WrapperPython()
  opWrapper.configure(params)
  opWrapper.start()
  datum = op.Datum()
  # get the image as input to openpose
  datum.cvInputData = image_with_id[1]
  opWrapper.emplaceAndPop(op.VectorDatum([datum]))
  return (image_with_id[0],datum.cvOutputData)
