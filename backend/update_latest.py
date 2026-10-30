import sys, asyncio
sys.path.append(r'd:\P-D-TEAM-final_updated\backend')
from motor.motor_asyncio import AsyncIOMotorClient
from server import detect_disease_unet, detect_disease_efficientnet, get_object, put_object, get_disease_info_and_practices
from disease_rules import combine_ensemble_models_and_rules

async def update_latest():
    client = AsyncIOMotorClient('mongodb://127.0.0.1:27017')
    db = client['sugarcane_db']
    latest = await db.detections.find().sort('created_at', -1).to_list(1)
    if not latest:
        print('No detections found')
        return
    det = latest[0]
    print('Found latest detection:', det.get('id'), det.get('created_at'))
    img_data, _ = get_object(det['image_path'])
    
    u_res = await detect_disease_unet(img_data)
    e_res = await detect_disease_efficientnet(img_data)
    comb = combine_ensemble_models_and_rules(u_res, e_res, img_data)
    
    final_disease = comb.get('disease')
    final_severity = comb.get('severity', 'medium')
    d_info, practices = get_disease_info_and_practices(final_disease)
    
    overlay_path = det.get('overlay_path')
    if comb.get('overlay_bytes'):
        put_object(overlay_path, comb['overlay_bytes'], 'image/jpeg')
        print('Updated overlay image in storage!')
        
    update_doc = {
        'ai_disease': final_disease,
        'ai_severity': final_severity,
        'disease': final_disease,
        'severity': final_severity,
        'is_co_infection': comb.get('is_co_infection', False),
        'primary_disease': comb.get('primary_disease', final_disease),
        'secondary_disease': comb.get('secondary_disease'),
        'ai_predictions': comb.get('predictions', []),
        'treatment': d_info['treatment'],
        'symptoms': d_info['symptoms'],
        'causes': d_info['causes'],
        'prevention': d_info['prevention'],
        'cultural_practices': practices.get('cultural', []),
        'mechanical_practices': practices.get('mechanical', []),
        'biological_practices': practices.get('biological', []),
        'chemical_practices': practices.get('chemical', []),
        'spray_timing': practices.get('timing', []),
    }
    
    res = await db.detections.update_one({'id': det['id']}, {'$set': update_doc})
    print('Update result modified_count:', res.modified_count)
    print('Successfully updated scan to:', final_disease)

asyncio.run(update_latest())
