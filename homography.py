import cv2
import glob
import numpy as np

image_path = glob.glob('images/*')
image_path.sort()

images = []

for i in range(0,len(image_path)):
    images.append(cv2.imread(image_path[i]))
print(len(images))

def find_homography(train_image, query_image):
    
    train_image = cv2.cvtColor(train_image, cv2.COLOR_BGR2GRAY)
    query_image = cv2.cvtColor(query_image, cv2.COLOR_BGR2GRAY)
    
    descriptor = cv2.SIFT.create()
    
    keypoints_train_image, features_train_image = descriptor.detectAndCompute(train_image,None)
    keypoints_query_image, features_query_image = descriptor.detectAndCompute(query_image,None)
    
    bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    
    raw_matches = bf.knnMatch(features_train_image, features_query_image, k=2)
    # print('Raw matches with KNN', len(raw_matches))
    
    knn_matches = []
    
    for m,n in raw_matches:
        if m.distance < n.distance * 0.75:
            knn_matches.append(m) 
    
    keypoints_train_img = np.float32([keypoint.pt for keypoint in keypoints_train_image])
    keypoints_query_img = np.float32([keypoint.pt for keypoint in keypoints_query_image])
    
    if len(knn_matches) > 4:
        points_train = np.float32([keypoints_train_img[m.queryIdx] for m in knn_matches])
        points_query = np.float32([keypoints_query_img[m.trainIdx] for m in knn_matches])
        
        (H, status) = cv2.findHomography(points_train, points_query, cv2.RANSAC, 4)
        
        return H
    
    else:
        return None
    
def decompose_homography(H):
    """
    РЕКОМЕНДОВАНО К ПЕРЕПРОВЕРКЕ НАПИСАНО ChatGPT
    """
    # Normalize homography matrix
    H = H / H[2, 2]
    
    # Extract rotation and scaling
    rotation_and_scale = H[:2, :2]
    scale = np.linalg.norm(rotation_and_scale[:, 0])
    rotation = rotation_and_scale / scale
    
    # Extract translation
    translation = H[:2, 2]
    
    # Calculate shear
    shear = np.arctan2(rotation[0, 1], rotation[1, 1])
    
    return rotation, scale, translation, shear

def compose_homography(rotation, scale, translation, shear):
    """
    РЕКОМЕНДОВАНО К ПЕРЕПРОВЕРКЕ НАПИСАНО ChatGPT
    """
    # Construct rotation matrix
    rotation_matrix = rotation
    
    # Construct shear matrix
    shear_matrix = np.array([[1, shear],
                             [0, 1]])
    
    # Construct scaling matrix
    scaling_matrix = np.diag([scale, scale])
    
    # Combine rotation, shear, and scaling matrices
    affine_matrix = np.matmul(rotation_matrix, shear_matrix)
    affine_matrix = np.matmul(affine_matrix, scaling_matrix)
    
    # Append translation vector to the affine matrix
    affine_matrix = np.column_stack([affine_matrix, translation])
    affine_matrix = np.vstack([affine_matrix, [0, 0, 1]])
    
    return affine_matrix

def trim(frame):
    #crop top
    if not np.sum(frame[0]):
        return trim(frame[1:])
    #crop bottom
    elif not np.sum(frame[-1]):
        return trim(frame[:-2])
    #crop left
    elif not np.sum(frame[:,0]):
        return trim(frame[:,1:]) 
    #crop right
    elif not np.sum(frame[:,-1]):
        return trim(frame[:,:-2])    
    return frame

pair = []

for i in range(0,24):
    homography_matrix = find_homography(train_image=images[i+1],query_image=images[i])
    
    if homography_matrix is None:
        pair.append({'Train image': i+1, 'Query image': i, 'Homography matrix': None, 
                     'Rotation matrix': None, 'Scale matrix': None, 'Translation matrix': None,
                     'Shear matrix': None})
        print(i+1)
    else:
        rotation, scale, translation, shear = decompose_homography(homography_matrix)
        pair.append({'Train image': i+1, 'Query image': i, 'Homography matrix': homography_matrix, 
                     'Rotation matrix': rotation, 'Scale matrix': scale, 'Translation matrix': translation,
                     'Shear matrix': shear})
        
x=0
y=0
print(len(pair))
result = images[0]

for i in range(0,24):
    x+= pair[i]["Translation matrix"][0]
    y+= pair[i]["Translation matrix"][1]
    
    composed_homography = compose_homography(pair[i]['Rotation matrix'],
                                             pair[i]['Scale matrix'],
                                             [x,y],
                                             pair[i]['Shear matrix'])
    
    width = result.shape[1] + images[i+1].shape[1]
    
    height = max(result.shape[0], images[i+1].shape[0])
    
    old_points = np.array([[[0,0]],[[0,images[i+1].shape[1]]],[[images[i+1].shape[0],0]],[[images[i+1].shape[0],images[i+1].shape[1]]]],np.float32)
    new_points = cv2.perspectiveTransform(old_points, composed_homography)
    result_st = cv2.warpPerspective(images[i+1], composed_homography, (width, height))
    
    result_st[0:result.shape[0],0:result.shape[1]] = result

    result = trim(result_st)
    result = result[0:result.shape[0],0:result.shape[1]-int(abs(new_points[2][0][0]-new_points[3][0][0]))]
    cv2.imwrite(f'res{i+1}.jpg',cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
    
    print(i)          